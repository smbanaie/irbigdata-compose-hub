from airflow.sdk import task, dag
from datetime import datetime

@dag(
    dag_id="12-new-etl",     # 👈 explicit DAG name
    schedule='@daily',          # Airflow 3 syntax
    start_date=datetime(2026, 5, 5),
    catchup=False,
    tags=["modern"],
)
def taskflow_xcom_example():

    @task
    def extract():
        return {"data": [1, 2, 3]}
    
    @task
    def transform(data):
        return [x * 2 for x in data['data']]
    
    @task
    def load(transformed_data):
        print(f"Loaded data: {transformed_data}")
    
    data = extract()
    transformed_data = transform(data)
    load(transformed_data)
    

xcom_example_dag = taskflow_xcom_example()
