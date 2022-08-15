import logging
from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.postgres_operator import PostgresOperator

 
create_table_sql_query = """CREATE TABLE IF NOT EXISTS GPU (名稱 varchar(255), 價格 varchar(255), 類型 varchar(255),款式 varchar(255),品牌名稱 varchar(255),記憶體 varchar(255),適用於 varchar(255), 保固期 varchar(255), 晶片 varchar(255), 商品規格 varchar(255));"""

def fetch_records():
    request = "SELECT 名稱 FROM gpu"
    hook = PostgresHook(postgres_conn_id = 'airflow_db', schema = 'airflow')
    connection = hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(request)
    sources = cursor.fetchall()
    logging.info(sources)
    return sources

DAG = DAG(
    dag_id="demo",
    start_date=datetime(2022, 2, 2),
    schedule_interval="@once",
    catchup=False,
)

create_table = PostgresOperator(
    sql = create_table_sql_query,
    task_id = "create_table_task",
    postgres_conn_id="airflow_db",
    dag=DAG
)

get_item_names = PythonOperator(
    task_id="get_item_names",
    python_callable=fetch_records,
)

create_table >> get_item_names
