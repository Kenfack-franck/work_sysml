import os
import google.generativeai as genai
from dotenv import load_dotenv
import warnings

# On ignore les avertissements de dépréciation pour avoir une sortie propre
warnings.filterwarnings("ignore")

# 1. Chargement de la clé
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERREUR : Pas de clé GEMINI_API_KEY dans le fichier .env")
    exit()

genai.configure(api_key=api_key)

print(f"🔑 Clé chargée : {api_key[:5]}...{api_key[-3:]}")
print("🚀 Démarrage du test de connectivité sur TOUS les modèles...\n")

working_models = []

try:
    # Récupère tous les modèles disponibles
    all_models = genai.list_models()
    
    for m in all_models:
        # On ne teste que les modèles qui savent générer du texte
        if 'generateContent' in m.supported_generation_methods:
            model_name = m.name
            print(f"👉 Test de : {model_name.ljust(40)}", end="")
            
            try:
                # TENTATIVE DE GÉNÉRATION
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Réponds juste 'OK'", request_options={"timeout": 5})
                
                if response.text:
                    print("✅ SUCCÈS (Fonctionne !)")
                    working_models.append(model_name)
                else:
                    print("⚠️  Réponse vide")
                    
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    print("❌ QUOTA DÉPASSÉ (Limit 0 ou épuisé)")
                elif "404" in error_msg:
                    print("⛔ NON TROUVÉ (Pas accès)")
                elif "400" in error_msg:
                    print("⚠️  NON SUPPORTÉ (Peut-être image seulement)")
                else:
                    # On affiche l'erreur courte pour pas polluer
                    print(f"💥 ERREUR : {error_msg.split('.')[0]}")

except Exception as global_e:
    print(f"\n❌ Erreur critique lors de la récupération de la liste : {global_e}")

print("\n" + "="*50)
print("🏆 RÉSUMÉ DES MODÈLES UTILISABLES IMMÉDIATEMENT")
print("="*50)

if working_models:
    for wm in working_models:
        # On nettoie le nom pour le config.py (enlève models/)
        clean_name = wm.replace("models/", "")
        print(f"✅ LLM_MODEL = \"{clean_name}\"")
else:
    print("❌ AUCUN modèle n'a fonctionné. Vérifie ta facturation ou crée une nouvelle clé dans un nouveau projet Google Cloud.")

print("="*50)