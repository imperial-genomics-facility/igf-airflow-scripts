from datetime import timedelta

import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.contrib.hooks.ssh_hook import SSHHook

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(dag_id='hpc_pipelines',
          catchup=False,
          schedule_interval="*/5 * * * *",
          max_active_runs=1,
          default_args=default_args)  ## TO DO

ssh_hook = SSHHook(ssh_conn_id='cx1_ssh_conn')

check_hpc_queue=SSHOperator(
    task_id='check_hpc_queue',
    dag=dag,
    ssh_hook=ssh_hook,
    do_xcom_push=True,
    command='source /etc/bashrc;qstat'
)

run_demultiplexing_pipeline = SSHOperator(
    task_id='run_demultiplexing_pipeline',
    dag=dag,
    ssh_hook=ssh_hook,
    command='bash /rds/general/user/igf/home/git_repo/IGF-cron-scripts/hpc/run_demultiplexing_pipeline.sh '
)

run_demultiplexing_pipeline.set_upstream(check_hpc_queue)

run_primary_analysis_pipeline = SSHOperator(
    task_id='run_primary_analysis_pipeline',
    dag=dag,
    ssh_hook=ssh_hook,
    command='bash /rds/general/user/igf/home/git_repo/IGF-cron-scripts/hpc/run_primary_analysis_pipeline.sh '
)

run_primary_analysis_pipeline.set_upstream(run_demultiplexing_pipeline)
