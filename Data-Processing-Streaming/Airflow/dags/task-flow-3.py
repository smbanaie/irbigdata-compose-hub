from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id="13-modern-parallel-tasks",     # 👈 explicit DAG name
    schedule='@daily',           # Airflow 3 syntax
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=["modern"],
)
def taskflow_parallel_tasks():

    @task
    def task_1():
        print("Task 1 executed")
    
    @task
    def task_2():
        print("Task 2 executed")
        return 1 
    
    @task
    def task_3():
        print("Task 3 executed")
    
    @task
    def final_task(upstream_input):
        print(f"Final task executed : {upstream_input}")

    t1 = task_1()
    t2 = task_2()
    t3 = task_3()

    # final_task depends on t2
    final_task(t2)

parallel_tasks_dag = taskflow_parallel_tasks()

