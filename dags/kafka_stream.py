import logging
import uuid
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka.errors import KafkaTimeoutError


default_args = {
    'owner': 'Suraj Shinde',
    'start_date': datetime(2024, 7, 1)
}


def get_data():
    import requests
    response = requests.get("https://randomuser.me/api/").json()
    return response['results'][0]


def format_data(response):
    data = {}
    location = response['location']
    data['id'] = uuid.uuid4()
    data['first_name'] = response['name']['first']
    data['last_name'] = response['name']['last']
    data['gender'] = response['gender']
    data['address'] = f"{str(location['street']['number'])} {location['street']['name']} " \
                      f"{location['city']}) {location['state']} {location['country']}"

    data['postcode'] = location['postcode']
    data['email'] = response['email']
    data['username'] = response['login']['username']
    data['dob'] = response['dob']['date']
    data['registered_date'] = response['registered']['date']
    data['phone'] = response['phone']
    data['picture'] = response['picture']['medium']

    return data


def stream_data():
    import json
    from kafka import KafkaProducer
    import time


    producer = KafkaProducer(bootstrap_servers=["broker:29092"],
                             max_block_ms=5000)
    curr_time = time.time()
    while True:
        if time.time() > curr_time + 60:
            break
        try:
            formatedData = format_data(get_data())
            producer.send('user_created', json.dumps(formatedData).encode('utf-8'))
            logging.INFO("Message sent successfully")
        except KafkaTimeoutError as e:
            logging.ERROR(f"Failed to send message: {e}")
            continue




with DAG('user_automation',
         default_args=default_args,
         schedule='@daily',
         catchup=False) as dag:
    streaming_task = PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data
    )

# stream_data()
