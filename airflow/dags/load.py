from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from airflow.utils.dates import days_ago
from sqlalchemy import create_engine
import pandas as pd
import configparser
import socket
from datetime import datetime

# Чтение конфигурации
config = configparser.ConfigParser()
config.read('/opt/airflow/dags/config.ini')

def get_postgresql_engine():
    # Подключение к PostgreSQL
    postgres_username = config['postgresql']['username']
    postgres_password = config['postgresql']['password']
    postgres_host = config['postgresql']['host']
    postgres_port = config['postgresql']['port']
    postgres_database = config['postgresql']['database']
    
    return create_engine(f'postgresql+psycopg2://{postgres_username}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_database}')

def get_mssql_engine():
    # Подключение к SQL Server
    mssql_username = config['sqlserver']['username']
    mssql_password = config['sqlserver']['password']
    mssql_server = config['sqlserver']['server']
    mssql_database = config['sqlserver']['database']
    
    return create_engine(f'mssql+pymssql://{mssql_username}:{mssql_password}@{mssql_server}/{mssql_database}')

def get_mysql_engine():
    # Подключение к MySQL
    mysql_username = config['mysql']['username']
    mysql_password = config['mysql']['password']
    mysql_host = config['mysql']['host']
    mysql_port = config['mysql']['port']
    mysql_database = config['mysql']['database']
    
    return create_engine(f'mysql+pymysql://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}')

def full_load_data(batch_size=1000):

    # Подключение к SQL Server
    mssql_engine = get_mssql_engine()

    # Подключение к PostgreSQL
    postgres_engine = get_postgresql_engine()

    # Запрос для извлечения данных из SQL Server
    sql_query = "SELECT COUNT(*) FROM dbo.full_data_airflow"
    total_records = pd.read_sql(sql_query, mssql_engine).iloc[0, 0]

    for offset in range(0, total_records, batch_size):
        # Извлечение данных порциями
        batch_query = f"SELECT *, getdate() as load_dt FROM dbo.full_data_airflow ORDER BY id OFFSET {offset} ROWS FETCH NEXT {batch_size} ROWS ONLY"
        df = pd.read_sql(batch_query, mssql_engine)

        if not df.empty:
            # Запись данных в PostgreSQL
            df.to_sql('full_data_airflow', postgres_engine, if_exists='append', index=False)
            print(f"Inserted {len(df)} records into PostgreSQL.")

def incremental_load_data(batch_size=1000):

    # Подключение к MySQL
    mysql_engine = get_mysql_engine()

    # Подключение к PostgreSQL
    postgres_engine = get_postgresql_engine()

    load_from = datetime.now()
    # Получение значения инкремента
    # Выполнение запроса
    with postgres_engine.connect() as connection:
        result = connection.execute("select coalesce(max(modified), '2000-01-01'::timestamp) as max from incremental_data_airflow;")
        
        # Получение скалярного значения
        load_from = result.scalar()
        print(f'Дата с: {load_from}')

    # Запрос для извлечения данных
    sql_query = f"SELECT COUNT(*) FROM incremental_data_airflow where modified > '{load_from}'"
    total_records = pd.read_sql(sql_query, mysql_engine).iloc[0, 0]

    for offset in range(0, total_records, batch_size):
        # Извлечение данных порциями
        batch_query = f"SELECT *, NOW() as load_dt FROM incremental_data_airflow where modified > '{load_from}' ORDER BY id LIMIT {batch_size} OFFSET {offset}"
        df = pd.read_sql(batch_query, mysql_engine)

        if not df.empty:
            # Запись данных в PostgreSQL
            df.to_sql('incremental_data_airflow', postgres_engine, if_exists='append', index=False)
            print(f"Inserted {len(df)} records into PostgreSQL.")

def f1():
    # Подключение к PostgreSQL
    postgres_engine = get_postgresql_engine()

    with postgres_engine.connect() as connection:
        result = connection.execute("call stg.f1();")


def f2():
    # Подключение к PostgreSQL
    postgres_engine = get_postgresql_engine()

    with postgres_engine.connect() as connection:
        result = connection.execute("call stg.f2();")

def remove_duplicates():
    # Подключение к PostgreSQL
    postgres_engine = get_postgresql_engine()

    with postgres_engine.connect() as connection:
        result = connection.execute('''
delete from
    full_data_airflow
where
    (id, load_dt) in
        (
            select
                id, load_dt
            from
                (
                    select
                        *, row_number() over (partition by id order by load_dt desc) as rn
                    from full_data_airflow
                ) as q
            where rn > 1
        );
''')

# Определение DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

dag = DAG(
    'ELT',
    default_args=default_args,
    description='DAG for transferring data from SQL Server to PostgreSQL using SQLAlchemy',
    schedule_interval='@daily',
)

with dag:
    with TaskGroup("load_data_to_staging", tooltip="Processing tasks group") as load_data:

        # Полная загрузка данных
        l1 = PythonOperator(
            task_id='full_load_from_sql_server',
            python_callable=full_load_data,
            op_kwargs={'batch_size': 1000},
            dag=dag,
        )

        # Инкрементальная загрузка данных
        l2 = PythonOperator(
            task_id='incremental_load_from_my_sql',
            python_callable=incremental_load_data,
            op_kwargs={'batch_size': 1000},
            dag=dag,
        )

    with TaskGroup("fact_run", tooltip="Processing tasks group") as load_fact:

        # Полная загрузка данных
        f1 = PythonOperator(
            task_id='fact_1',
            python_callable=f1,
            dag=dag,
        )

        # Инкрементальная загрузка данных
        f2 = PythonOperator(
            task_id='fact_2',
            python_callable=f2,
            dag=dag,
        )

# Инкрементальная загрузка данных
remove_duplicates_task = PythonOperator(
    task_id='remove_duplicates',
    python_callable=remove_duplicates,
    dag=dag,
)

load_data >> [load_fact, remove_duplicates_task]