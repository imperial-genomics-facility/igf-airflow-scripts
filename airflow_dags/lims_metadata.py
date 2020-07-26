import airflow
from airflow import DAG
from datetime import timedelta
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
    'schedule_interval':'@daily',
}

dag = DAG(dag_id='lims_metadata',
          catchup=False,
          schedule_interval="@daily",
          max_active_runs=1,
          default_args=default_args)

cx1_ssh_hook = SSHHook(ssh_conn_id='cx1_ssh_conn')


check_hpc_queue=SSHOperator(
    task_id='check_hpc_queue',
    dag=dag,
    ssh_hook=cx1_ssh_hook,
    do_xcom_push=True,
    command='source /etc/bashrc;qstat'
)

submit_metadata_fetch_job = \
  SSHOperator(
    task_id = 'submit_metadata_fetch_job',
    dag = dag,
    ssh_hook = cx1_ssh_hook,
    do_xcom_push=True,
    command = 'source /etc/bashrc;qsub /rds/general/user/igf/home/git_repo/IGF-cron-scripts/hpc/lims_metadata/fetch_lims_metadata_qsub.sh '
)

submit_metadata_fetch_job.set_upstream(check_hpc_queue)
