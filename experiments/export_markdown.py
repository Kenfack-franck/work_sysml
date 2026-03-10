#!/usr/bin/env python3
"""
Export d'une session SysML-Agent en fichiers Markdown.

Usage:
    python experiments/export_markdown.py --session-id UUID --output-dir experiments/01_test/style_formel/
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Le package 'requests' est requis. Installez-le avec : pip install requests")
    sys.exit(1)

API_BASE_URL = "http://localhost:8000"


def fetch_export(session_id: str) -> dict:
    """Appelle GET /api/v2/export/{session_id} et retourne le JSON."""
    url = f"{API_BASE_URL}/api/v2/export/{session_id}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def write_level_markdown(level: str, level_data: dict, session_name: str, description: str, output_dir: Path) -> None:
    """Écrit le fichier Markdown pour un niveau donné."""
    exchanges = level_data.get("exchanges", [])
    if not exchanges:
        return

    lines = [
        f"# Niveau {level.capitalize()} — {session_name}",
        "",
        "## Description fournie",
        f"> {description}",
        "",
    ]

    for i, exchange in enumerate(exchanges, 1):
        operation = exchange.get("operation", f"exchange_{i}")
        prompt = exchange.get("prompt_sent", "")
        raw = exchange.get("llm_response_raw", "")
        sysml = exchange.get("sysml_code", "")
        timestamp = exchange.get("timestamp", "")

        # Libellé lisible pour l'opération
        op_label_map = {
            "generate_json": "Description → JSON",
            "generate_sysml": "JSON → Code SysML v2",
            "patch_json": "Patch JSON",
        }
        op_label = op_label_map.get(operation, operation)

        lines += [
            f"## Échange {i} : {op_label}",
            "",
        ]
        if timestamp:
            lines += [f"*{timestamp}*", ""]

        if prompt:
            lines += [
                "### Prompt envoyé au LLM",
                "",
                "```",
                prompt,
                "```",
                "",
            ]

        if raw:
            lines += [
                "### Réponse brute du LLM",
                "",
                "```",
                raw,
                "```",
                "",
            ]

        if sysml:
            lines += [
                "### Code SysML v2 généré",
                "",
                "```sysml",
                sysml,
                "```",
                "",
            ]

    output_file = output_dir / f"{level}.md"
    output_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ {output_file}")


def write_description_markdown(description: str, session_name: str, output_dir: Path) -> None:
    """Écrit le fichier description.md."""
    lines = [
        f"# {session_name}",
        "",
        "## Description originale",
        "",
        description,
        "",
    ]
    output_file = output_dir / "description.md"
    output_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Exporte une session SysML-Agent en fichiers Markdown."
    )
    parser.add_argument("--session-id", required=True, help="UUID de la session à exporter")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Dossier de sortie (ex: experiments/01_test/style_formel/)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Récupération de la session {args.session_id}...")
    try:
        data = fetch_export(args.session_id)
    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de se connecter à {API_BASE_URL}. Vérifiez que le backend est démarré.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP : {e}")
        sys.exit(1)

    session_name = data.get("session_name") or args.session_id
    description = data.get("description", "")
    levels = data.get("levels", {})
    metadata = data.get("metadata", {})

    print(f"Session : {session_name}")
    print(f"Échanges totaux : {metadata.get('total_exchanges', 0)}")
    print(f"Dossier de sortie : {output_dir}")
    print()

    # Écrire description.md
    write_description_markdown(description, session_name, output_dir)

    # Écrire un fichier par niveau
    for level, level_data in levels.items():
        if level_data.get("exchanges"):
            write_level_markdown(level, level_data, session_name, description, output_dir)

    print()
    print(f"Export terminé dans : {output_dir}")


if __name__ == "__main__":
    main()
