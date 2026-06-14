# AGENTS.md — IA Khawarizmi Pro
# Version : 2.0.0
# Emplacement : Racine du projet
# Rôle : System Prompt permanent pour tout agent IA
#         intervenant sur ce projet

##############################################################
# SECTION 0 — IDENTITÉ DU PROJET
##############################################################

Tu travailles sur **IA Khawarizmi Pro**.

C'est une plateforme éducative IA destinée aux lycéens
algériens préparant le Bac Sciences Naturelles.

Stack technique officiel :
- Backend  : FastAPI + Python 3.12
- Base     : PostgreSQL 16 + pgvector
- Cache    : Redis 7
- IA       : Gemini 2.5 Flash (principal)
             OpenAI GPT (fallback 1)
             Pattern matching local (fallback 2)
             JSON de sécurité (fallback 3)
- Auth     : JWT uniquement (python-jose + bcrypt)
- Répétion : Algorithme FSRS Graph
- Deploy   : Railway (Docker)
- Frontend : Next.js 16 + React 19 + TailwindCSS 4
- Mobile   : React Native + Expo 56

##############################################################
# SECTION 1 — RÈGLES ABSOLUES (NE JAMAIS VIOLER)
##############################################################

## 1.1 Sécurité

- JAMAIS de clé API, token ou mot de passe dans le code
- JAMAIS de valeur par défaut pour SECRET_KEY en production
- JAMAIS de fichier .env commité dans Git
- TOUJOURS lever une ValueError si SECRET_KEY absent :

  ```python
  secret_key = os.environ.get("SECRET_KEY")
  if not secret_key:
      raise ValueError(
          "SECRET_KEY non défini. Arrêt du serveur."
      )
  ```

- TOUJOURS utiliser **JWT uniquement** pour l'auth
- JAMAIS de double système auth (pas de Supabase Auth,
  pas de localStorage token, pas de demo_local_token)

## 1.2 Architecture Code

- main.py : **maximum 100 lignes** (imports + init + lifespan)
- Un fichier = Une responsabilité unique
- Migrations : **Alembic uniquement** (jamais SQL inline)
- Dépendances : **versions épinglées** dans requirements.txt

Structure obligatoire du backend :

```
khawarizmi-backend/
├── main.py              (max 100 lignes)
├── config.py            (Settings Pydantic)
├── auth.py              (JWT uniquement)
├── database.py          (connexion DB)
├── cache.py             (Redis uniquement)
├── schemas/
│   ├── user.py
│   ├── session.py
│   ├── flashcard.py
│   └── mindmap.py
├── models/
│   ├── user.py
│   ├── concept.py
│   └── session.py
├── routes/
│   ├── auth.py
│   ├── chat.py
│   ├── evaluate.py
│   ├── flashcards.py
│   ├── mindmap.py
│   ├── sessions.py
│   └── payment.py
├── services/
│   ├── rag_service.py
│   ├── ai_service.py
│   ├── fsrs_service.py
│   ├── mindmap_service.py
│   └── payment_service.py
├── migrations/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_chat.py
│   ├── test_mindmap.py
│   └── test_fsrs.py
├── scripts/
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 1.3 Ports et Déploiement

- TOUJOURS utiliser `$PORT` dynamique (Railway l'injecte)
- JAMAIS de port hardcodé dans railway.toml
- Configuration correcte obligatoire :

  ```dockerfile
  # Dockerfile
  CMD ["sh", "-c",
       "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
  ```

  ```toml
  # railway.toml
  [deploy]
  startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
  ```

## 1.4 Rate Limiting

- TOUJOURS appliquer slowapi sur /api/chat et /api/evaluate
- Quotas obligatoires :
  - Gratuit  : 20 req/heure chat — 15 req/heure evaluate
  - Premium  : 100 req/heure chat — 80 req/heure evaluate

## 1.5 SQL et Base de Données

- JAMAIS de concaténation de chaînes dans les requêtes SQL
- JAMAIS de `IN :param` avec tuple (bug asyncpg)
- TOUJOURS utiliser `ANY(:array)` pour les listes :

  ```python
  # Correct
  await db.execute(
      text("SELECT * FROM t WHERE id = ANY(:ids)"),
      {"ids": list(my_ids)}
  )
  ```

##############################################################
# SECTION 2 — LES 4 PILIERS PÉDAGOGIQUES
##############################################################

Toute réponse de l'IA au tuteur doit respecter ces 4 piliers.
Ne jamais générer de code qui les contourne.

## Pilier 1 — Simplification (Feynman)
- Explication simple avant technique
- Analogie concrète obligatoire
- Méthode Socratique intégrée (guider, pas donner)

## Pilier 2 — Rappel Actif (Active Recall)
- Questions L1 (restitution) → L2 (application)
         → L3 (type Bac)
- Jamais donner la réponse dans la même réponse

## Pilier 3 — Répétition Espacée (FSRS)
- Flashcards : Recto (max 15 mots) / Verso (max 30 mots)
- Intégration obligatoire avec l'algorithme FSRS Graph
- Plan : J+0 / J+1 / J+3 / J+7 / J+14 / J+30

## Pilier 4 — Mind Map Dynamique (JSON)
- Schéma JSON obligatoire (voir Section 4)
- Connexion automatique avec FSRS
- 3 niveaux de rendu :
  A) Textuel (toujours)
  B) Mermaid.js (si supporté)
  C) JSON Dynamique (interface avancée)

##############################################################
# SECTION 3 — POLITIQUE RAG STRICTE
##############################################################

- L'IA répond UNIQUEMENT à partir du contexte RAG fourni
- Si contexte vide → répondre :
  "Je n'ai pas trouvé cette information dans la base.
   Consulte ton manuel officiel."
- JAMAIS inventer une définition, formule, corrigé,
  barème ou référence ONEC

Exception de Navigation :
  Si l'élève demande la liste des chapitres ou
  le programme officiel → autoriser les connaissances
  générales avec mention obligatoire de la source.

##############################################################
# SECTION 4 — SCHÉMA JSON MIND MAP (RÉFÉRENCE)
##############################################################

```json
{
  "id": "string-unique",
  "titre": "NOM DU CHAPITRE",
  "matiere": "SVT | Maths | Physique...",
  "filiere": "Sciences Naturelles...",
  "racine": {
    "id": "string",
    "label": "string — max 5 mots",
    "type": "concept|definition|formule|processus|exception",
    "niveau": 0,
    "importance": "critique|haute|moyenne",
    "bac_frequent": true,
    "flashcard_auto": true,
    "maitrise_eleve": 0,
    "couleur": "#E74C3C",
    "enfants": [],
    "liens": []
  },
  "liens_transversaux": [
    {
      "source": "id_noeud",
      "target": "id_noeud",
      "relation": "string",
      "type": "causal|dependance|opposition|inclusion"
    }
  ],
  "metadata": {
    "genere_le": "ISO date",
    "version": "1.0",
    "source_rag": "nom du chunk"
  }
}
```

Règles Mind Map :
- Maximum 3 niveaux de profondeur
- Maximum 7 enfants par nœud
- Maximum 5 mots par label
- flashcard_auto = true si importance critique ou haute
- Couleurs : critique=#E74C3C haute=#F39C12 moyenne=#3498DB

Endpoints obligatoires :
- POST /api/mindmap/generate      (générer)
- GET  /api/mindmap/{id}          (récupérer)
- PATCH /api/mindmap/{node}/maitrise (mettre à jour)
- GET  /api/mindmap/{id}/weak     (nœuds faibles)

##############################################################
# SECTION 5 — GITIGNORE OBLIGATOIRE
##############################################################

Le .gitignore racine doit contenir exactement :

```gitignore
# Environnement — CRITIQUE
**/.env
**/.env.*
!**/.env.example

# Secrets
*.pem
*.key
*.p12
secrets/

# Backups et données lourdes
*.backup_*
*.backup_inject_*
*.bak

# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/

# Node
node_modules/
.next/
dist/
.expo/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Modèles IA lourds
models/
*.zip
*.tar.gz
*.gguf

# Logs
*.log
logs/
```

Encodage : UTF-8 obligatoire (jamais UTF-16)

##############################################################
# SECTION 6 — TESTS OBLIGATOIRES
##############################################################

- conftest.py obligatoire dans tests/
- pytest-asyncio obligatoire
- Couverture minimum : 70%
- CI/CD GitHub Actions obligatoire

tests/conftest.py minimum :

```python
import pytest
import asyncio
from httpx import AsyncClient
from main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    async with AsyncClient(
        app=app,
        base_url="http://test"
    ) as ac:
        yield ac
```

Tests obligatoires par module :
- test_auth.py     : register, login, token invalide
- test_chat.py     : RAG valide, RAG vide, rate limit
- test_mindmap.py  : génération, structure JSON,
                     flashcard auto, FSRS sync
- test_fsrs.py     : création carte, schedule, weak nodes

##############################################################
# SECTION 7 — MONITORING
##############################################################

- Sentry obligatoire en production
- Health check endpoint /health obligatoire :

  ```json
  {
    "status": "healthy",
    "version": "2.0.0",
    "database": "connected",
    "redis": "connected",
    "ai_model": "gemini-2.5-flash",
    "fallback_active": false,
    "timestamp": "ISO date"
  }
  ```

- Alertes obligatoires :
  Erreur 500 → alerte immédiate
  Rate limit massif → alerte
  Clé API invalide → alerte
  Fallback IA activé → log

##############################################################
# SECTION 8 — COMPORTEMENT DE L'AGENT
##############################################################

## Avant de générer du code, toujours vérifier :

  [ ] Aucune clé API dans le code
  [ ] SECRET_KEY lève ValueError si absent
  [ ] main.py reste sous 100 lignes
  [ ] Un fichier = Une responsabilité
  [ ] Migrations via Alembic
  [ ] Dépendances épinglées
  [ ] Rate limiting présent si endpoint IA
  [ ] JWT vérifié sur chaque endpoint protégé
  [ ] ANY(:array) au lieu de IN :tuple
  [ ] $PORT dynamique (jamais hardcodé)

## Si une règle est violée dans la demande :

  → Signaler AVANT de générer le code :
    "⚠️ Cette demande viole la règle [X].
     Voici la version corrigée conforme
     au prompt développeur Khawarizmi Pro."

## Format de réponse code :

  1. Fichier concerné (chemin complet)
  2. Code complet (jamais de "..." ou "[reste du code]")
  3. Commandes d'installation si nouvelles dépendances
  4. Test correspondant si applicable

## Langue :

  - Commentaires dans le code : Français
  - Variables et fonctions : Anglais (snake_case)
  - Noms de fichiers : Anglais (snake_case)

##############################################################
# SECTION 9 — PRIORITÉS ACTUELLES DU PROJET
##############################################################

État au moment de la rédaction de ce fichier :

CRITIQUE — À faire immédiatement :
  [ ] Régénérer toutes les clés API exposées
  [ ] Réécrire .gitignore en UTF-8 propre
  [ ] Corriger les ports ($PORT partout)
  [ ] Unifier l'auth sur JWT uniquement
  [ ] Ajouter rate limiting sur /api/chat
      et /api/evaluate

IMPORTANT — À faire ce mois :
  [ ] Refactorer main.py (1296 lignes → modules)
  [ ] Épingler les dépendances requirements.txt
  [ ] Configurer Alembic pour les migrations
  [ ] Créer conftest.py et activer les tests
  [ ] Configurer GitHub Actions CI/CD

STRATÉGIQUE — À faire ce trimestre :
  [ ] Implémenter Mind Map JSON dynamique
  [ ] Connecter Next.js frontend au backend
  [ ] Ajouter Sentry monitoring
  [ ] Implémenter /health endpoint
  [ ] Connecter Mind Map ↔ FSRS

##############################################################
# FIN — AGENTS.md v2.0.0 — IA KHAWARIZMI PRO
# Ce fichier est la source de vérité du projet.
# Toute décision de développement s'y réfère.
##############################################################
