import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Charge la clé
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") # Vérifie que c'est bien le nom dans ton .env

if not api_key:
    print("❌ ERREUR: Pas de clé trouvée dans le fichier .env")
    exit()

# 2. Configure l'API
genai.configure(api_key=api_key)

print(f"🔍 Recherche des modèles disponibles pour ta clé...\n")

try:
    # 3. Récupère la liste
    models = genai.list_models()
    found = False
    for m in models:
        # On ne veut que les modèles qui génèrent du texte
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ DISPONIBLE : {m.name}")
            found = True
            
    if not found:
        print("⚠️ Aucun modèle de génération de texte trouvé. Vérifie tes droits API.")
        
except Exception as e:
    print(f"❌ ERREUR CRITIQUE : {e}")


