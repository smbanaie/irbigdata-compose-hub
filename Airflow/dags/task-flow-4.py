from airflow.decorators import dag, task
from datetime import datetime


@dag(
    dag_id="14-modern-branch",     # 👈 explicit DAG name
    schedule='@daily',
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=["modern"],
)
def taskflow_branching_example():

    @task
    def choose_branch() -> str:
        # Return the task_id of the branch to follow
        return "even_task" if datetime.now().day % 2 == 0 else "odd_task"

    @task.branch
    def branch_path(choice: str):
        return choice   # must return task_id(s)

    @task
    def even_task():
        print("Even day task")

    @task
    def odd_task():
        print("Odd day task")

    # Build task graph
    choice = choose_branch()
    branch = branch_path(choice)
    branch >> [even_task(), odd_task()]


branching_dag = taskflow_branching_example()
