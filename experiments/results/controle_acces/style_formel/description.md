# Contrôle accès - style_formel

## Description originale

Le système de contrôle d'accès du bâtiment est composé des éléments suivants. Un lecteur de badges RFID est installé à chaque point d'entrée. Il lit l'identifiant du badge et transmet cette information au contrôleur central. Le contrôleur central reçoit les identifiants des badges, interroge la base de données des autorisations, et prend la décision d'autoriser ou refuser l'accès. En cas d'autorisation, le contrôleur envoie une commande d'ouverture à la serrure électrique. La serrure électrique verrouille ou déverrouille la porte selon la commande reçue. Une caméra de surveillance est positionnée à chaque entrée et enregistre en continu. En cas de tentative d'accès refusée, le contrôleur déclenche une alerte sur le poste de sécurité. Le système doit fonctionner 24 heures sur 24 et 7 jours sur 7. Le temps entre la lecture du badge et le déverrouillage de la porte ne doit pas dépasser 2 secondes.
