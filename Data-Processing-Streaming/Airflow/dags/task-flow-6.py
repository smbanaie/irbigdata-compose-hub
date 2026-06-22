from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id="19-depends-on-past-demo",
    schedule='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=True,   # 👈 must be True so multiple runs are created
    tags=["depends_on_past"],
)
def depends_on_past_dag():

    @task(
        depends_on_past=True,   # 👈 key setting
        retries=0               # no retries, so failure will stop the chain
    )
    def sequential_task(execution_date=None):
        print(f"Running task for {execution_date}")

    sequential_task()


test_depends_on_past = depends_on_past_dag()
