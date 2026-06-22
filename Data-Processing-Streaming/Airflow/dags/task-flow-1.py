from airflow.sdk import task, dag
from datetime import datetime

@dag(
    dag_id="11-hello_world_dag",     # 👈 explicit DAG name
    schedule='*/5 * * * *',      # Airflow 3 syntax
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=["modern"],
)
def taskflow_hello_world():
    
    @task
    def hello():
        print("Hello, TaskFlow API!")
    
    hello()

hello_world_dag = taskflow_hello_world()
