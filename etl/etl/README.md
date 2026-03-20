# ETL HealthAI Coach

Pipeline d'ingestion de données de santé/fitness vers PostgreSQL. Il tourne en continu via un scheduler (APScheduler) qui exécute tous les pipelines au démarrage puis selon un cron configurable.

## Ce que ça fait

4 pipelines + 1 générateur, dans cet ordre :

1. **exercisedb** importe un catalogue d'exercices depuis un JSON → table `exercises`
2. **nutrition** importe un dataset de valeurs nutritionnelles depuis un CSV → table `nutrition_entries`
3. **gym_tracking** importe des données de séances de gym et métriques corporelles → tables `exercise_entries` + `biometric_entries`
4. **diet_recommendations** importe des recommandations diététiques par profil patient → table `diet_recommendations`
5. **faker_users** génère des utilisateurs fictifs avec Faker → table `users`

Chaque pipeline suit le même flux : `extract → clean → export CSV → load en base`. Les lignes rejetées (données invalides) sont exportées séparément dans `data/processed/`. Chaque run est tracé dans la table `etl_logs`.

Les `INSERT` utilisent `ON CONFLICT DO NOTHING` donc le pipeline est idempotent on peut le relancer autant de fois qu'on veut sans doublon.

## Lancer avec Docker (normal)

```bash
# Depuis la racine du projet
docker compose up -d db
docker compose --profile etl up etl

# Logs en temps réel
docker logs -f healthai_etl
```

Par défaut le scheduler tourne les pipelines au démarrage puis toutes les nuits à 2h. Pour tester avec un interval court :

```bash
CRON_SCHEDULE="*/2 * * * *" docker compose --profile etl up etl
```

## Lancer en local (dev)

```bash
cd etl
pip install -r requirements.txt

# One-shot (sans scheduler)
DB_HOST=localhost python main.py

# Avec scheduler
DB_HOST=localhost python scheduler.py
```

## Variables d'environnement

| Variable        | Défaut                | Description                                 |
| --------------- | --------------------- | ------------------------------------------- |
| `DB_HOST`       | `db`                  | Hôte PostgreSQL (mettre `localhost` en dev) |
| `DB_PORT`       | `5432`                |                                             |
| `DB_NAME`       | `healthcoach`         |                                             |
| `DB_USER`       | `healthcoach`         |                                             |
| `DB_PASSWORD`   | `healthcoach`         |                                             |
| `CRON_SCHEDULE` | `0 2 * * *`           | Expression cron pour la planification       |
| `DATA_DIR`      | `/app/data/raw`       | Dossier des fichiers sources                |
| `PROCESSED_DIR` | `/app/data/processed` | Exports CSV (rejects, clean)                |

## Vérifier que ça a tourné

```bash
docker exec healthai_db psql -U healthcoach -d healthcoach \
  -c "SELECT source_name, started_at, status, rows_inserted, rows_rejected FROM etl_logs ORDER BY started_at DESC LIMIT 10;"
```

## Tests et lint

```bash
cd etl

ruff check .
ruff format .

pytest
pytest tests/test_cleaners_nutrition.py  # un seul fichier
pytest -k "test_clean"                   # filtre par nom
```

## Ajouter un pipeline

1. Créer `pipelines/mon_pipeline.py` avec un dict `PIPELINE` (clés : `name`, `extract`, `clean`, `tables`)
2. Créer l'extractor dans `extractors/` si besoin
3. Créer le cleaner dans `cleaners/`
4. Importer et ajouter dans `pipelines/__init__.py`
