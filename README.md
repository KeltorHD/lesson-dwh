Airflow и Nifi как инструменты построения хранилищ данных

Каталоги:
- databases (все субд для примеров)
- nifi (сервис и драйвера для него)
- airflow (Dockerfile, директории, конфигурация и зависимости python)


Первое что нужно сделать - создать сеть lesson-dwh:
docker network create lesson-dwh

Запуск nifi (запускать в директории nifi):
docker compose up -d

Запуск airflow (запускать в директории airflow):
docker compose up -d --build