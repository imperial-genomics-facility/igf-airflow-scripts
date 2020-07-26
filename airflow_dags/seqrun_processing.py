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

dag = DAG(dag_id='seqrun_processing',
          catchup=False,
          schedule_interval="@hourly",
          max_active_runs=1,
          default_args=default_args)  ## TO DO

ssh_hook = SSHHook(ssh_conn_id='orwell_ssh_conn')
cx1_ssh_hook = SSHHook(ssh_conn_id='cx1_ssh_conn')

switch_off_project_barcode = SSHOperator(
    task_id = 'switch_off_project_barcode',
    dag = dag,
    ssh_hook = ssh_hook,
    command = 'bash /home/igf/igf_code/IGF-cron-scripts/orwell/switch_off_project_barcode_check.sh '
)

change_samplesheet_for_run = SSHOperator(
    task_id = 'change_samplesheet_for_run',
    dag = dag,
    ssh_hook = ssh_hook,
    command = 'bash /home/igf/igf_code/IGF-cron-scripts/orwell/change_samplesheet_for_seqrun.sh '
)

change_samplesheet_for_run.set_upstream(switch_off_project_barcode)

restart_seqrun_processing = SSHOperator(
    task_id = 'restart_seqrun_processing',
    dag = dag,
    ssh_hook = ssh_hook,
    command = 'bash /home/igf/igf_code/IGF-cron-scripts/orwell/restart_seqrun_processing.sh '
)

restart_seqrun_processing.set_upstream(change_samplesheet_for_run)

register_project_metadata = SSHOperator(
    task_id = 'register_project_metadata',
    dag = dag,
    ssh_hook = ssh_hook,
    command = 'bash /home/igf/igf_code/IGF-cron-scripts/orwell/register_metadata.sh '
)

register_project_metadata.set_upstream(restart_seqrun_processing)

find_new_seqrun = SSHOperator(
    task_id = 'find_new_seqrun',
    dag = dag,
    ssh_hook = ssh_hook,
    command = 'bash /home/igf/igf_code/IGF-cron-scripts/orwell/find_new_seqrun.sh '
)

find_new_seqrun.set_upstream(register_project_metadata)

seed_demultiplexing_pipe = SSHOperator(
    task_id = 'seed_demultiplexing_pipe',
    dag = dag,
    ssh_hook = cx1_ssh_hook,
    command = 'bash /rds/general/user/igf/home/git_repo/IGF-cron-scripts/hpc/seed_demultiplexing_pipeline.sh '
)

seed_demultiplexing_pipe.set_upstream(find_new_seqrun)
