from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id="15-expanding",     # 👈 explicit DAG name
    schedule='@daily',           # Airflow 3 syntax
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=["modern"],
)
def taskflow_dynamic_tasks():

    @task
    def process_item(item):
        print(f"Processing {item}")

    items = ["item_1", "item_2", "item_3", "item_10", "item_20", "item_30"]

    # Dynamically create a task for each item
    process_item.expand(item=items)

dynamic_tasks_dag = taskflow_dynamic_tasks()
