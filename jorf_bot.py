#!/usr/bin/env python3
"""
Bot pour surveiller le Journal Officiel et envoyer un résumé des articles pertinents
pour la préparation du concours INSP via Alertzy.
"""

import os
import feedparser
import requests
from openai import OpenAI
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JORFBot:
    def __init__(self):
        self.rss_url = "https://droit.org/flux/jorf.rss"
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.alertzy_key = os.getenv('ALERTZY_KEY')
        
    def fetch_rss_feed(self):
        """Récupère le flux RSS du Journal Officiel"""
        try:
            logger.info("Récupération du flux RSS du Journal Officiel...")
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:
                logger.warning(f"Problème de parsing RSS: {feed.bozo_exception}")
            
            logger.info(f"Flux récupéré avec {len(feed.entries)} articles")
            
            # Log de tous les titres reçus du flux RSS
            logger.info("Tous les titres reçus du flux RSS:")
            for i, entry in enumerate(feed.entries, 1):
                title = entry.get('title', 'Sans titre')
                logger.info(f"  {i}. {title}")
            
            return feed
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du flux RSS: {e}")
            return None
    
    def filter_relevant_articles(self, feed):
        """Filtre les articles pertinents pour la préparation INSP"""
        if not feed or not feed.entries:
            return []
        
        relevant_keywords = [
            "politique publique", "fonction publique", "administration", "gouvernement",
            "ministre", "secrétaire d'état", "préfet", "directeur", "nomination",
            "décret", "loi", "ordonnance", "arrêté", "circulaire",
            "concours", "recrutement", "formation", "INSP", "ENA",
            "budget", "finance", "économie", "social", "santé", "éducation",
            "justice", "intérieur", "défense", "affaires étrangères",
            "transition écologique", "numérique", "innovation"
        ]
        
        relevant_articles = []
        
        for entry in feed.entries:
            title = entry.get('title', '').lower()
            description = entry.get('description', '').lower()
            content = f"{title} {description}"
            
            # Vérifier si l'article contient des mots-clés pertinents
            if any(keyword in content for keyword in relevant_keywords):
                relevant_articles.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'description': entry.get('description', ''),
                    'published': entry.get('published', '')
                })
        
        logger.info(f"{len(relevant_articles)} articles pertinents trouvés sur {len(feed.entries)}")
        return relevant_articles
    
    def generate_summary_with_ai(self, articles):
        """Génère un résumé des articles avec OpenAI en divisant en plusieurs appels"""
        if not articles:
            return "Aucun article pertinent trouvé aujourd'hui."
        
        # Diviser les articles en chunks pour éviter le dépassement de contexte
        chunk_size = 20  # Nombre d'articles par chunk (≈ 6000 tokens)
        chunks = [articles[i:i + chunk_size] for i in range(0, len(articles), chunk_size)]
        
        logger.info(f"Articles divisés en {len(chunks)} chunks de {chunk_size} articles maximum")
        
        all_summaries = []
        
        for chunk_idx, chunk in enumerate(chunks, 1):
            logger.info(f"Traitement du chunk {chunk_idx}/{len(chunks)} avec {len(chunk)} articles")
            
            # Préparer le contenu pour ce chunk
            articles_text = ""
            for i, article in enumerate(chunk, 1):
                title = article['title'][:200] + "..." if len(article['title']) > 200 else article['title']
                description = article['description'][:400] + "..." if len(article['description']) > 400 else article['description']
                articles_text += f"\n{i}. {title}\n   Lien: {article['link']}\n   Description: {description}\n"
            
            # Log des titres de ce chunk
            logger.info(f"Titres du chunk {chunk_idx}:")
            for i, article in enumerate(chunk, 1):
                title = article['title'][:100] + "..." if len(article['title']) > 100 else article['title']
                logger.info(f"  {i}. {title}")
            
            prompt = f"""
Tu es un assistant spécialisé dans l'analyse du Journal Officiel français pour des stagiaires préparant le concours de l'INSP (Institut National du Service Public).

Voici une partie des articles du Journal Officiel d'aujourd'hui (chunk {chunk_idx}/{len(chunks)}) :

{articles_text}

Analyse ces articles et crée un résumé structuré et informatif pour des stagiaires préparant le concours INSP. 

Concentre-toi sur :
- Les textes importants pour la vie publique, notamment en lien avec l'actualité
- Les politiques publiques nouvelles ou modifiées
- Les évolutions institutionnelles
- Tres tres tres peu de nominations sauf si elles sont vraiment hyper importantes (ministres surtout, ou personnages politiques importants), et pas de mobilites
- Si il te reste de la place dans ton contexte tu peux ajouter des choses moins importantes
- Pour des groupes de textes tres similaires tu peux tout résumer en une seule phrase

Format de sortie :
- Utilise des emojis pour rendre le message plus attractif
- Structure avec des titres clairs
- Sois hyper concis mais informatif
- Adapte le ton pour une notification mobile
- Limite à 1000 caractères maximum pour ce chunk, mais si tu n'as rien tu n'es pas obligé de remplir l'espace pour rien

Commence par "📰 JOURNAL OFFICIEL - Partie {chunk_idx} 📰"
"""

            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Tu es un expert en droit administratif et en préparation aux concours de la fonction publique française."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                chunk_summary = response.choices[0].message.content
                all_summaries.append(chunk_summary)
                logger.info(f"Chunk {chunk_idx} traité avec succès")
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement du chunk {chunk_idx}: {e}")
                all_summaries.append(f"Erreur lors du traitement du chunk {chunk_idx}: {str(e)}")
        
        # Concaténer tous les résumés
        if len(all_summaries) == 1:
            final_summary = all_summaries[0]
        else:
            final_summary = "📰 JOURNAL OFFICIEL - Résumé du jour 📰\n\n"
            for i, summary in enumerate(all_summaries, 1):
                # Nettoyer le résumé (enlever les en-têtes répétées)
                clean_summary = summary.replace(f"📰 JOURNAL OFFICIEL - Partie {i} 📰", "").strip()
                final_summary += f"{clean_summary}\n\n"
        
        logger.info(f"Résumé final généré avec {len(all_summaries)} chunks")
        return final_summary
    
    def send_to_alertzy(self, message):
        """Envoie le message via Alertzy"""
        if not self.alertzy_key:
            logger.error("Clé Alertzy manquante")
            return False
        
        try:
            url = "https://alertzy.app/send"
            data = {
                "accountKey": self.alertzy_key,
                "title": "📰 Journal Officiel - Résumé INSP",
                "message": message,
                "priority": "normal"
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logger.info("Message envoyé avec succès via Alertzy")
                return True
            else:
                logger.error(f"Erreur lors de l'envoi Alertzy: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi Alertzy: {e}")
            return False
    
    def run(self):
        """Fonction principale du bot"""
        logger.info("Démarrage du bot JORF")
        
        # Récupérer le flux RSS
        feed = self.fetch_rss_feed()
        if not feed:
            logger.error("Impossible de récupérer le flux RSS")
            return
        
        # Filtrer les articles pertinents
        relevant_articles = self.filter_relevant_articles(feed)
        
        if not relevant_articles:
            message = "📰 JOURNAL OFFICIEL - Résumé du jour 📰\n\nAucun article particulièrement pertinent pour la préparation INSP aujourd'hui."
        else:
            # Générer le résumé avec l'IA
            summary = self.generate_summary_with_ai(relevant_articles)
            message = summary
        
        # Envoyer via Alertzy
        if self.send_to_alertzy(message):
            logger.info("Bot exécuté avec succès")
        else:
            logger.error("Échec de l'envoi via Alertzy")

def main():
    """Point d'entrée principal"""
    bot = JORFBot()
    bot.run()

if __name__ == "__main__":
    main()
