from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

# Функция, которая будет выполняться
def print_hello():
    print("Hello, World!")

# Определение DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

dag = DAG(
    'hello_world_dag',
    default_args=default_args,
    description='A simple Hello World DAG',
    schedule_interval='@once',  # Запускать один раз
)

# Определение задачи
hello_task = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
    dag=dag,
)

# Установка зависимостей (в данном случае нет, так как только одна задача)
hello_task