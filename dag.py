from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd
import sqlite3

# Configurações padrão do DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definindo a DAG
dag = DAG(
    dag_id='etl_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
)

def extract_transform_load():
    # Diretório do CSV
    transformed_csv_path = 'transformed_data.csv'  # Substitua pelo caminho adequado
    
    # Extrair dados do banco de dados SQLite
    db_path = 'hospital.db'  # Substitua pelo caminho adequado
    conn = sqlite3.connect(db_path)
    try:
        query = "SELECT * FROM Patient;"  # Verifique o nome da tabela
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    
    # Transformar dados (se necessário)
    # Aqui você pode adicionar qualquer transformação necessária, por exemplo:
    # df['new_column'] = df['existing_column'].apply(some_transformation_function)
    
    # Salvar dados transformados em CSV
    df.to_csv(transformed_csv_path, index=False)

# Tarefa do DAG
etl_task = PythonOperator(
    task_id='etl_task',
    python_callable=extract_transform_load,
    dag=dag,
)

etl_task  # Certifique-se de que a tarefa seja retornada, para que o Airflow a reconheça

