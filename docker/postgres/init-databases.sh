#!/usr/bin/env bash
set -euo pipefail
for service in APP MLFLOW AIRFLOW; do
    user_var="${service}_DB_USER"
    password_var="${service}_DB_PASSWORD"
    name_var="${service}_DB_NAME"
    psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
        --set=ON_ERROR_STOP=1 --set=db_user="${!user_var}" \
        --set=db_password="${!password_var}" --set=db_name="${!name_var}" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'db_user', :'db_password') \gexec
SELECT format('CREATE DATABASE %I OWNER %I', :'db_name', :'db_user') \gexec
REVOKE CONNECT ON DATABASE :"db_name" FROM PUBLIC;
GRANT CONNECT ON DATABASE :"db_name" TO :"db_user";
SQL
done
