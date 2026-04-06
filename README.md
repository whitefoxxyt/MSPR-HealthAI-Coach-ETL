# MSPR HealthAI Coach - ETL

Microservice ETL pour la plateforme HealthAI Coach.

Stack : Python 3.12 + APScheduler + pandas + psycopg2.

Ce service est independant de l'API et du service AUTH. Il se connecte a la base de donnees MSPR-DB via le reseau Docker `mspr_data_network`.

## Demarrage

```bash
cp .env.example .env
# Remplir DB_PASSWORD avec le mot de passe MSPR-DB

# Prerequis : MSPR-DB doit etre running (cree le reseau mspr_data_network)
docker compose up -d
```

Les pipelines s'executent au demarrage puis selon le cron configure.

## Variables d'environnement

| Variable        | Defaut             | Description                                        |
| --------------- | ------------------ | -------------------------------------------------- |
| `DB_HOST`       | `mspr-healthai-db` | Container name MSPR-DB (mettre `localhost` en dev) |
| `DB_PORT`       | `5432`             | Port PostgreSQL                                    |
| `DB_NAME`       | `healthai`         | Nom de la base                                     |
| `DB_USER`       | `healthai_user`    | Utilisateur PostgreSQL                             |
| `DB_PASSWORD`   | -                  | Mot de passe (obligatoire)                         |
| `CRON_SCHEDULE` | `0 2 * * *`        | Planification des runs                             |

## Pipelines

4 pipelines + 1 generateur de donnees fictives :

| Pipeline              | Source                                    | Tables cibles                                 |
| --------------------- | ----------------------------------------- | --------------------------------------------- |
| `exercisedb`          | `data/raw/exercisedb/exercises.json`      | `exercises`                                   |
| `nutrition_dataset`   | `daily_food_nutrition_dataset.csv`        | `nutrition_entries`                           |
| `gym_tracking`        | 2 CSVs gym                                | `exercise_entries`, `biometric_entries`       |
| `diet_recommendations`| `diet_recommendations_dataset.csv`        | `diet_recommendations`                        |
| `faker_users`         | genere via Faker                          | `users`                                       |

Chaque run est trace dans la table `etl_logs`.

## Tests et lint

```bash
cd etl

ruff check .
ruff format .

pytest
```

## Ports

| Service     | Port hote |
|-------------|-----------|
| healthai_etl | aucun (worker) |

## Reseau Docker

Ce compose rejoint le reseau `mspr_data_network` cree par MSPR-DB :

```yaml
networks:
  mspr_data_network:
    external: true
```
