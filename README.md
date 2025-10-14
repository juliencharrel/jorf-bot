# 🤖 JORF Bot - Surveillance du Journal Officiel

Un bot automatisé qui surveille quotidiennement le Journal Officiel français et envoie un résumé des articles pertinents pour la préparation du concours INSP via Alertzy.

## 🎯 Fonctionnalités

- **Surveillance automatique** : Vérifie le flux RSS du Journal Officiel chaque jour à 8h00
- **Filtrage intelligent** : Identifie les articles pertinents pour la préparation INSP
- **Analyse IA** : Utilise OpenAI pour générer des résumés structurés et informatifs
- **Notifications Alertzy** : Envoie les résumés via Alertzy (notifications push)
- **Format optimisé** : Messages adaptés pour mobile avec emojis et structure claire

## 🚀 Installation et Configuration

### 1. Prérequis

- Un compte GitHub
- Une clé API OpenAI
- Un compte Alertzy (gratuit)

### 2. Configuration des secrets GitHub

Dans votre repository GitHub, allez dans **Settings > Secrets and variables > Actions** et ajoutez :

```
OPENAI_API_KEY=votre_cle_openai_ici
ALERTZY_KEY=votre_cle_alertzy_ici
```

### 3. Configuration Alertzy

1. Créez un compte sur [Alertzy.app](https://alertzy.app)
2. Obtenez votre clé API dans les paramètres
3. Ajoutez-la aux secrets GitHub

### 4. Test local (optionnel)

```bash
# Cloner le repository
git clone <votre-repo>
cd jorf-bot

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp env.example .env
# Éditer .env avec vos vraies valeurs

# Tester le bot
python test_bot.py
```

## 📋 Structure du projet

```
jorf-bot/
├── .github/
│   └── workflows/
│       └── jorf-bot.yml          # Workflow GitHub Actions
├── jorf_bot.py                   # Script principal du bot
├── test_bot.py                   # Script de test local
├── requirements.txt              # Dépendances Python
├── env.example                   # Exemple de configuration
└── README.md                     # Ce fichier
```

## 🔧 Personnalisation

### Modifier les mots-clés de filtrage

Dans `jorf_bot.py`, modifiez la liste `relevant_keywords` pour ajuster les critères de sélection.

### Changer l'heure d'exécution

Dans `.github/workflows/jorf-bot.yml`, modifiez la ligne cron :

```yaml
- cron: '0 7 * * *'  # 8h00 (UTC+1)
```

## 🛠️ Dépannage

### Le bot ne s'exécute pas

1. Vérifiez que les secrets GitHub sont correctement configurés
2. Consultez les logs dans l'onglet "Actions" de votre repository
3. Testez manuellement avec "workflow_dispatch"

### Aucune notification reçue

1. Vérifiez que votre clé Alertzy est valide
2. Testez avec le script de test local
3. Vérifiez que l'app Alertzy est installée sur votre téléphone

### Erreurs OpenAI

1. Vérifiez que votre clé API OpenAI est valide
2. Vérifiez que vous avez des crédits disponibles
3. Consultez les logs pour plus de détails

## 📊 Monitoring

Le bot génère des logs détaillés que vous pouvez consulter dans :
- **GitHub Actions** : Onglet "Actions" de votre repository
- **Logs locaux** : Si vous exécutez le bot en local

## 🔒 Sécurité

- Les clés API sont stockées comme secrets GitHub (sécurisé)
- Aucune donnée sensible n'est commitée dans le code
- Le bot ne stocke aucune donnée personnelle

---

**Note** : Ce bot est conçu pour aider les stagiaires préparant le concours INSP en leur fournissant un résumé quotidien des informations importantes du Journal Officiel. Il ne remplace pas une veille personnelle et régulière des sources officielles.
