"""
Service RAG pour l'indexation et la recherche de code SysML v2.
Utilise ChromaDB pour le stockage vectoriel et sentence-transformers pour les embeddings.
"""

import logging
from pathlib import Path
from typing import List, Dict

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class RAGService:
    """Service de RAG pour indexer et rechercher du code SysML v2."""

    def __init__(self, chroma_dir: Path, embedding_model: str, sysml_repo_path: Path):
        """
        Initialise le service RAG.

        Args:
            chroma_dir: Répertoire de persistance ChromaDB
            embedding_model: Nom du modèle sentence-transformers
            sysml_repo_path: Chemin vers le dépôt SysML-v2-Release
        """
        self.chroma_dir = chroma_dir
        self.sysml_repo_path = sysml_repo_path
        self.embedding_model_name = embedding_model

        # Crée le répertoire ChromaDB s'il n'existe pas
        chroma_dir.mkdir(parents=True, exist_ok=True)

        # Initialise le modèle d'embeddings
        logger.info(f"Chargement du modèle d'embeddings : {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)

        # Initialise ChromaDB avec persistance
        logger.info(f"Initialisation de ChromaDB dans : {chroma_dir}")
        self.client = chromadb.PersistentClient(
            path=str(chroma_dir),
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        # Crée ou récupère la collection
        self.collection = self.client.get_or_create_collection(
            name="sysml_v2_docs",
            metadata={"description": "SysML v2 code examples and training files"}
        )

        logger.info(f"Collection 'sysml_v2_docs' prête ({self.collection.count()} documents)")

    def index_sysml_files(self, force: bool = False) -> Dict:
        """
        Indexe les fichiers SysML du dépôt.

        Args:
            force: Si True, supprime la collection existante et ré-indexe

        Returns:
            Dictionnaire avec le statut et les statistiques
        """
        # Vérifie si déjà indexé
        existing_count = self.collection.count()
        if existing_count > 0 and not force:
            logger.info(f"Collection déjà indexée avec {existing_count} chunks. Skip.")
            return {"status": "skipped", "existing_chunks": existing_count}

        # Si force=True, supprime et recrée la collection
        if force:
            logger.info("Force=True : suppression de la collection existante")
            self.client.delete_collection("sysml_v2_docs")
            self.collection = self.client.get_or_create_collection(
                name="sysml_v2_docs",
                metadata={"description": "SysML v2 code examples and training files"}
            )

        # Trouve les fichiers .sysml dans training/ et examples/
        training_dir = self.sysml_repo_path / "sysml" / "src" / "training"
        examples_dir = self.sysml_repo_path / "sysml" / "src" / "examples"

        sysml_files = []
        if training_dir.exists():
            sysml_files.extend([
                (f, "training") for f in training_dir.rglob("*.sysml")
            ])
        if examples_dir.exists():
            sysml_files.extend([
                (f, "example") for f in examples_dir.rglob("*.sysml")
            ])

        if not sysml_files:
            logger.warning(f"Aucun fichier .sysml trouvé dans {self.sysml_repo_path}")
            return {"status": "error", "message": "No .sysml files found"}

        logger.info(f"Indexation de {len(sysml_files)} fichiers .sysml")

        # Indexe chaque fichier
        total_chunks = 0
        for file_path, category in sysml_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                chunks = self._split_sysml_code(content, chunk_size=1500, chunk_overlap=200)

                # Prépare les données pour ChromaDB
                ids = [f"{file_path.name}_{i}" for i in range(len(chunks))]
                embeddings = self.embedder.encode(chunks, convert_to_numpy=True).tolist()
                metadatas = [
                    {
                        "source_file": str(file_path.relative_to(self.sysml_repo_path)),
                        "chunk_index": i,
                        "category": category,
                    }
                    for i in range(len(chunks))
                ]

                # Ajoute à ChromaDB
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=chunks,
                    metadatas=metadatas,
                )

                total_chunks += len(chunks)
                logger.info(f"  ✓ {file_path.name} : {len(chunks)} chunks")

            except Exception as e:
                logger.error(f"  ✗ Erreur lors de l'indexation de {file_path.name} : {e}")

        logger.info(f"Indexation terminée : {len(sysml_files)} fichiers, {total_chunks} chunks")
        return {
            "status": "ok",
            "files_indexed": len(sysml_files),
            "chunks_total": total_chunks,
        }

    def _split_sysml_code(self, code: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Découpe le code SysML en chunks en respectant la structure des blocs.

        Args:
            code: Code SysML complet
            chunk_size: Taille cible d'un chunk en caractères
            chunk_overlap: Nombre de caractères de chevauchement entre chunks

        Returns:
            Liste de chunks
        """
        # Sépare par lignes
        lines = code.split("\n")

        # Identifie les blocs (lignes se terminant par '}' seul ou avec des espaces)
        blocks = []
        current_block = []

        for line in lines:
            current_block.append(line)
            # Fin de bloc : ligne contenant uniquement '}' (avec espaces optionnels)
            if line.strip() == "}":
                blocks.append("\n".join(current_block))
                current_block = []

        # Ajoute le dernier bloc si non vide
        if current_block:
            blocks.append("\n".join(current_block))

        # Regroupe les blocs en chunks
        chunks = []
        current_chunk = []
        current_size = 0

        for block in blocks:
            block_size = len(block)

            # Si un seul bloc dépasse chunk_size, le garder entier
            if block_size > chunk_size and not current_chunk:
                chunks.append(block)
                continue

            # Si ajouter ce bloc dépasse chunk_size, finalise le chunk actuel
            if current_size + block_size > chunk_size and current_chunk:
                chunk_text = "\n".join(current_chunk)
                chunks.append(chunk_text)

                # Overlap : prend les derniers caractères pour le prochain chunk
                overlap_text = chunk_text[-chunk_overlap:] if chunk_overlap > 0 else ""
                current_chunk = [overlap_text] if overlap_text else []
                current_size = len(overlap_text)

            # Ajoute le bloc au chunk actuel
            current_chunk.append(block)
            current_size += block_size + 1  # +1 pour le \n

        # Ajoute le dernier chunk
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def search(self, query: str, top_k: int = 8) -> List[Dict]:
        """
        Recherche les chunks les plus similaires à la query.

        Args:
            query: Requête utilisateur
            top_k: Nombre de résultats à retourner

        Returns:
            Liste de dictionnaires avec content, source_file, score
        """
        # Calcule l'embedding de la query
        query_embedding = self.embedder.encode([query], convert_to_numpy=True).tolist()

        # Recherche dans ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        # Formate les résultats
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "content": doc,
                    "source_file": results["metadatas"][0][i]["source_file"],
                    "score": 1.0 - results["distances"][0][i],  # Convertit distance en score
                })

        return formatted_results

    def get_stats(self) -> Dict:
        """
        Retourne des statistiques sur la collection.

        Returns:
            Dictionnaire avec le nombre de documents et les fichiers sources
        """
        count = self.collection.count()

        # Récupère tous les métadonnées pour extraire les fichiers uniques
        if count > 0:
            all_data = self.collection.get(limit=count)
            unique_files = list(set(
                meta["source_file"] for meta in all_data["metadatas"]
            ))
        else:
            unique_files = []

        return {
            "total_chunks": count,
            "unique_files": len(unique_files),
            "files": sorted(unique_files),
        }
