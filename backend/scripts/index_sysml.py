#!/usr/bin/env python3
"""
Script pour forcer la ré-indexation des fichiers SysML v2.
Usage: python -m backend.scripts.index_sysml
"""

import sys
from pathlib import Path

# Ajoute le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.services.rag_service import RAGService


def main():
    print("=" * 60)
    print("Ré-indexation forcée des fichiers SysML v2")
    print("=" * 60)

    # Crée le service RAG
    rag = RAGService(
        chroma_dir=settings.CHROMA_DIR,
        embedding_model=settings.EMBEDDING_MODEL,
        sysml_repo_path=settings.SYSML_REPO_PATH,
    )

    # Lance l'indexation forcée
    print(f"\nDépôt SysML : {settings.SYSML_REPO_PATH}")
    print(f"ChromaDB    : {settings.CHROMA_DIR}")
    print(f"Modèle      : {settings.EMBEDDING_MODEL}")
    print("\nIndexation en cours...")

    result = rag.index_sysml_files(force=True)

    # Affiche les résultats
    print("\n" + "=" * 60)
    if result["status"] == "ok":
        print("✓ Indexation réussie !")
        print(f"  - Fichiers indexés : {result['files_indexed']}")
        print(f"  - Chunks totaux    : {result['chunks_total']}")
    else:
        print(f"✗ Erreur : {result.get('message', 'Unknown error')}")

    # Affiche les stats
    print("\n" + "=" * 60)
    print("Statistiques de la collection :")
    stats = rag.get_stats()
    print(f"  - Total chunks     : {stats['total_chunks']}")
    print(f"  - Fichiers uniques : {stats['unique_files']}")
    print(f"  - Fichiers sources :")
    for file in stats['files'][:10]:  # Limite à 10 pour la lisibilité
        print(f"    • {file}")
    if len(stats['files']) > 10:
        print(f"    ... et {len(stats['files']) - 10} autres")

    print("=" * 60)


if __name__ == "__main__":
    main()
