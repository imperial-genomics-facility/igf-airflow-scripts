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
    'schedule_interval':'@hourly',
}

dag = DAG(dag_id='disk_usage_check',
          catchup=False,
          schedule_interval="@hourly",
          max_active_runs=1,
          default_args=default_args)

orwell_ssh_hook = SSHHook(ssh_conn_id='orwell_ssh_conn')
cx1_ssh_hook = SSHHook(ssh_conn_id='cx1_ssh_conn')
woolf_ssh_hook = SSHHook(ssh_conn_id='woolf_ssh_conn')
eliot_ssh_hook = SSHHook(ssh_conn_id='eliot_ssh_conn')
igf_lims_ssh_hook = SSHHook(ssh_conn_id='igf_lims_ssh_conn')

check_orwell_disk = SSHOperator(
    task_id = 'check_orwell_disk',
    dag = dag,
    ssh_hook = orwell_ssh_hook,
    command = 'bash /home/igf/igf_code/IGF-cron-scripts/orwell/orwell_disk_usage.sh '
)

check_eliot_disk = SSHOperator(
    task_id = 'check_eliot_disk',
    dag = dag,
    ssh_hook = eliot_ssh_hook,
    command = 'bash /home/igf/git_repos/IGF-cron-scripts/eliot/eliot_disk_usage.sh '
)

check_eliot_disk.set_upstream(check_orwell_disk)

check_woolf_disk = SSHOperator(
    task_id = 'check_woolf_disk',
    dag = dag,
    ssh_hook = woolf_ssh_hook,
    command = 'bash /home/igf/git_repos/IGF-cron-scripts/woolf/woolf_disk_usage.sh '
)

check_woolf_disk.set_upstream(check_eliot_disk)

check_igf_lims_disk = SSHOperator(
    task_id = 'check_igf_lims_disk',
    dag = dag,
    ssh_hook = igf_lims_ssh_hook,
    command = 'bash /home/igf/github/IGF-cron-scripts/igf_lims/igf_lims_disk_usage.sh '
)

check_igf_lims_disk.set_upstream(check_woolf_disk)


merge_disk_usage = SSHOperator(
    task_id = 'merge_disk_usage',
    dag = dag,
    ssh_hook = eliot_ssh_hook,
    command = 'bash /home/igf/git_repos/IGF-cron-scripts/eliot/merge_disk_usage.sh '
)

merge_disk_usage.set_upstream(check_igf_lims_disk)

internal_usage = SSHOperator(
    task_id = 'internal_usage',
    dag = dag,
    ssh_hook = eliot_ssh_hook,
    command = 'bash /home/igf/git_repos/IGF-cron-scripts/eliot/internal_usage.sh '
)

internal_usage.set_upstream(merge_disk_usage)
