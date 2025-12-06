from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Path นี้คือ path ภายใน Docker (ซึ่ง Map ออกมาที่เครื่องจริงของคุณ)
TRIGGER_FILE_PATH = "/opt/airflow/dags/trigger_ddproperty.txt"

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'trigger_ddproperty_local',
    default_args=default_args,
    description='สร้างไฟล์ Trigger เพื่อสั่งให้เครื่อง Local เริ่มดูดข้อมูล DDProperty',
    schedule='0 6 * * *', # รันทุก 6 โมงเช้า
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['trigger', 'local', 'ddproperty'],
) as dag:

    # Task: สร้างไฟล์ .txt เปล่าๆ ขึ้นมา
    create_trigger = BashOperator(
        task_id='create_trigger_file',
        bash_command=f'touch {TRIGGER_FILE_PATH} && echo "Start" > {TRIGGER_FILE_PATH} && echo "สร้าง Trigger File สำเร็จ รอเครื่อง Local ทำงาน..."',
    )

    create_trigger