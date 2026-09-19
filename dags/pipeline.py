from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="weather_risk_pipeline",
    start_date=datetime(2026, 9, 16),
    schedule="@daily",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["weather", "pipeline"],
) as dag:

    extraction = BashOperator(
        task_id="extraction",
        bash_command=(
            "cd /opt/airflow && "
            "python /opt/airflow/src/extraction.py"
        ),
    )

    transformation = BashOperator(
        task_id="transformation",
        bash_command=(
            "cd /opt/airflow && "
            "python /opt/airflow/src/transformation.py"
        ),
    )

    feature_engineering = BashOperator(
        task_id="feature_engineering",
        bash_command=(
            "cd /opt/airflow && "
            "python /opt/airflow/src/feature_engineering.py"
        ),
    )

    load_database = BashOperator(
        task_id="load_database",
        bash_command=(
            "cd /opt/airflow && "
            "python /opt/airflow/src/database.py"
        ),
    )

    extraction >> transformation >> feature_engineering >> load_database