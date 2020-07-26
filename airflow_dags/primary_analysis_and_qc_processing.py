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
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(dag_id='primary_analysis_and_qc_processing',
          catchup=False,
          schedule_interval="@hourly",
          max_active_runs=1,
          default_args=default_args)  ## TO DO

ssh_hook = SSHHook(ssh_conn_id='cx1_ssh_conn')
orwell_ssh_hook = SSHHook(ssh_conn_id='orwell_ssh_conn')

update_exp_metadata = SSHOperator(
    task_id = 'update_exp_metadata',
    dag = dag,
    ssh_hook = ssh_hook,
    command = 'bash /rds/general/user/igf/home/git_repo/IGF-cron-scripts/hpc/update_exp_metadata.sh '
)

find_new_exp_for_analysis = SSHOperator(
    task_id = 'find_new_exp_for_analysis',
    dag = dag,
    ssh_hook = orwell_ssh_hook,
    command = 'bash /home/igf/igf_code/IGF-cron-scripts/orwell/find_new_exp_for_analysis.sh '
)

find_new_exp_for_analysis.set_upstream(update_exp_metadata)

seed_analysis_pipeline = SSHOperator(
    task_id = 'seed_analysis_pipeline',
    dag = dag,
    ssh_hook = ssh_hook,
    command = 'bash /rds/general/user/igf/home/git_repo/IGF-cron-scripts/hpc/seed_analysis_pipeline.sh '
)

seed_analysis_pipeline.set_upstream(find_new_exp_for_analysis)
