#!/usr/bin/env python3
"""
Automatise le test complet du pipeline SysML v2 sur plusieurs styles de description.

Usage:
    python experiments/run_experiment.py [options]

Options:
    --descriptions-dir  Dossier contenant les fichiers .txt (default: experiments/descriptions/controle_acces/)
    --output-dir        Dossier de sortie (default: experiments/results/controle_acces/)
    --backend-url       URL du backend (default: http://localhost:8000)
    --dry-run           Affiche ce qui serait fait sans appeler l'API
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Le package 'requests' est requis. Installez-le avec : pip install requests")
    sys.exit(1)

LEVELS = ["operational", "functional", "logical", "technical"]

LEVEL_DESCRIPTIONS = {
    "functional": "Générer le niveau fonctionnel à partir du niveau opérationnel",
    "logical": "Générer le niveau logique à partir du niveau fonctionnel",
    "technical": "Générer le niveau technique à partir du niveau logique",
}


def post_json(url: str, body: dict, dry_run: bool = False) -> dict:
    """Effectue un POST JSON et retourne la réponse parsée."""
    if dry_run:
        return {"session_id": "DRY-RUN-SESSION-ID", "level": body.get("level", ""), "model": {}, "sysml_code": ""}
    response = requests.post(url, json=body, timeout=120)
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise RuntimeError(f"HTTP {response.status_code} : {detail}")
    return response.json()


def run_style(style_name: str, description: str, output_dir: Path, backend_url: str, dry_run: bool) -> dict:
    """
    Exécute le pipeline complet pour un style donné.
    Retourne {"style", "session_id", "status", "failed_at"}.
    """
    print(f"\n=== Test du style : {style_name} ===")
    result = {"style": style_name, "session_id": "", "status": "✅ Complet", "failed_at": ""}

    session_id = None

    for i, level in enumerate(LEVELS):
        # --- Génération ---
        try:
            body = {
                "level": level,
                "use_rag": True,
            }
            if level == "operational":
                body["description"] = description
                body["session_name"] = f"Contrôle accès - {style_name}"
            else:
                body["description"] = LEVEL_DESCRIPTIONS[level]
                body["session_id"] = session_id

            if dry_run:
                print(f"  [DRY-RUN] POST {backend_url}/api/v2/generate  body={json.dumps({**body, 'description': body['description'][:40] + '...'})}")
            data = post_json(f"{backend_url}/api/v2/generate", body, dry_run=dry_run)

            if session_id is None:
                session_id = data.get("session_id", "DRY-RUN-SESSION-ID")
                result["session_id"] = session_id
            print(f"  ✓ {level.capitalize()} généré (session: {session_id})")

        except Exception as e:
            print(f"  ❌ Erreur génération {level} : {e}")
            result["status"] = f"❌ Erreur à {level} (generate)"
            result["failed_at"] = f"{level}/generate"
            return result

        # --- Validation ---
        try:
            validate_body = {"session_id": session_id, "level": level}
            if dry_run:
                print(f"  [DRY-RUN] POST {backend_url}/api/v2/validate  body={json.dumps(validate_body)}")
            post_json(f"{backend_url}/api/v2/validate", validate_body, dry_run=dry_run)
            print(f"  ✓ {level.capitalize()} validé")

        except Exception as e:
            print(f"  ❌ Erreur validation {level} : {e}")
            result["status"] = f"❌ Erreur à {level} (validate)"
            result["failed_at"] = f"{level}/validate"
            return result

    # --- Export Markdown ---
    style_output_dir = output_dir / style_name
    style_output_dir.mkdir(parents=True, exist_ok=True)

    export_script = Path(__file__).parent / "export_markdown.py"
    cmd = [
        sys.executable, str(export_script),
        "--session-id", session_id,
        "--output-dir", str(style_output_dir),
    ]
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(cmd)}")
    else:
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"  ✓ Export Markdown terminé → {style_output_dir}/")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Export Markdown échoué : {e.stderr.strip()}")
            # Non-fatal : on continue

    return result


def write_readme(output_dir: Path, results: list) -> None:
    """Crée le fichier README.md de synthèse."""
    lines = [
        "# Expérience — Contrôle d'accès bâtiment",
        "",
        f"*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "## Styles de description testés",
        "",
        "| Style | Session ID | Statut |",
        "|---|---|---|",
    ]
    for r in results:
        lines.append(f"| {r['style']} | {r['session_id']} | {r['status']} |")

    lines += [
        "",
        "## Comment consulter les résultats",
        "",
        "Chaque sous-dossier contient les fichiers Markdown avec les prompts envoyés et les réponses du LLM pour chaque niveau MBSE.",
        "",
        "```",
        f"{output_dir}/",
        "├── README.md",
    ]
    for r in results:
        lines.append(f"├── {r['style']}/")
        for lvl in LEVELS:
            lines.append(f"│   ├── {lvl}.md")
        lines.append(f"│   └── description.md")
    lines.append("```")

    readme_path = output_dir / "README.md"
    readme_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✅ README créé : {readme_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Automatise le test du pipeline SysML v2 sur plusieurs styles de description."
    )
    parser.add_argument(
        "--descriptions-dir",
        default="experiments/descriptions/controle_acces/",
        help="Dossier contenant les fichiers .txt de description",
    )
    parser.add_argument(
        "--output-dir",
        default="experiments/results/controle_acces/",
        help="Dossier de sortie pour les Markdown exportés",
    )
    parser.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        help="URL du backend FastAPI",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche ce qui serait fait sans appeler l'API",
    )
    args = parser.parse_args()

    descriptions_dir = Path(args.descriptions_dir)
    output_dir = Path(args.output_dir)

    if not descriptions_dir.exists():
        print(f"❌ Dossier de descriptions introuvable : {descriptions_dir}")
        sys.exit(1)

    txt_files = sorted(descriptions_dir.glob("*.txt"))
    if not txt_files:
        print(f"❌ Aucun fichier .txt trouvé dans {descriptions_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print("⚠️  Mode DRY-RUN activé — aucun appel API ne sera effectué.\n")

    print(f"Fichiers trouvés : {[f.name for f in txt_files]}")
    print(f"Dossier de sortie : {output_dir}")
    print(f"Backend : {args.backend_url}")

    all_results = []

    for idx, txt_file in enumerate(txt_files):
        style_name = txt_file.stem  # ex: "style_formel"
        description = txt_file.read_text(encoding="utf-8").strip()

        result = run_style(
            style_name=style_name,
            description=description,
            output_dir=output_dir,
            backend_url=args.backend_url,
            dry_run=args.dry_run,
        )
        all_results.append(result)

        # Pause entre les styles pour éviter le rate limiting Gemini
        if idx < len(txt_files) - 1:
            if args.dry_run:
                print("  [DRY-RUN] sleep(5) — rate limiting pause")
            else:
                print("  ⏳ Pause 5 secondes (rate limiting)...")
                time.sleep(5)

    write_readme(output_dir, all_results)

    print("\n=== Résumé ===")
    for r in all_results:
        print(f"  {r['style']:30s}  {r['status']}")

    print("\nExpérience terminée.")


if __name__ == "__main__":
    main()
