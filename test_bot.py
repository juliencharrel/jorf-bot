#!/usr/bin/env python3
"""
Script de test pour le bot JORF - permet de tester en local
"""

import os
from dotenv import load_dotenv
from jorf_bot import JORFBot

def main():
    """Test local du bot"""
    print("🧪 Test du bot JORF en local...")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Vérifier les variables d'environnement
    required_vars = ['OPENAI_API_KEY', 'ALERTZY_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variables d'environnement manquantes: {', '.join(missing_vars)}")
        print("💡 Créez un fichier .env avec vos clés API")
        return
    
    print("✅ Variables d'environnement OK")
    
    # Créer et exécuter le bot
    bot = JORFBot()
    bot.run()
    
    print("✅ Test terminé")

if __name__ == "__main__":
    main()
