from airflow.models import Variable
from airflow.hooks.base_hook import BaseHook
from datetime import timedelta
import ast
from textwrap import dedent
# from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import json
from confluent_kafka.avro import AvroProducer, CachedSchemaRegistryClient
import elasticapm
from confluent_kafka import avro
import requests
from utility import KafkaSchemaNotFound

from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator 
# from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago
from requests.api import head
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization

from airflow.utils.log.logging_mixin import LoggingMixin

##----------------------------- Functions -----------------------------------

def get_companies(**kwargs): 
    logger = LoggingMixin().log

    clientAPM = elasticapm.Client(service_name='ETL-Basics', service_version="1.0",
                                  server_url=Variable.get("APM-Server"))
    try : 
        conn = Variable.get("URL-API-Mabna")
        logger.info("^-"*25)
        logger.info(f"Connection Base URL : {conn}")
        endpoint=f'/{Variable.get("Mabna-Companies-Endpoint")}'
        logger.info(f"Endpoint : {endpoint}")
        headers = {
            'Authorization': f'Basic {Variable.get("Mabna-Basic-Token")}',
            }
        count = 100
        increment_size=100
        skip=0
        flag=True
        data= []
        API_URL= f"{conn}{endpoint}"
        logger.info(f"Mabna URL in Request :{API_URL}")
        while flag :
            payload = {'_count': f'{count}', '_skip': f'{skip}', '_expand':'state,exchange'}
            r = requests.get(API_URL, params=payload, headers=headers)
            if r.status_code == 200:
                logger.info("^--"*20)
                logger.info(f'Successfully read {count} data from {skip} to {skip+increment_size}')
                skip += increment_size
            return_data = r.json()["data"]
            if len(return_data) == 0 :
                flag = False
            data.extend(return_data)
        return data
    except Exception as ex : 
        clientAPM.capture_exception()
        logger.error(ex)
        raise ex


def delivery_report(err, msg):
    logger = LoggingMixin().log

    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        logger.error('Message delivery failed: {}'.format(err))
        
    else:
        logger.info('Message delivered To {} [{}]'.format(msg.topic(), msg.partition()))



def produce_companies(**kwargs):
    logger = LoggingMixin().log

    clientAPM = elasticapm.Client(service_name='ETL-Basics', service_version="1.0",
                                  server_url=Variable.get("APM-Server"))
    logger.info("*-"*25)
    key_schema_str = '''
    {"namespace": "saba.references.basics.company",
    "name": "key",
    "type": "record",
    "fields" : [
        {
        "name" : "id",
        "type" : "string"
        }
    ]}'''
     
    logger.info (f"Key Schema Config : {key_schema_str} ")
    key_schema = avro.loads(key_schema_str)
    logger.info("*&"*25)
    TOPIC= Variable.get("Topic-Companies")
    logger.info(f"Topic : {TOPIC}")
    SUBJECT= Variable.get("Schema-Subject-Companies").strip()
    logger.info("-@-"*25)
    logger.info(f"Schema of Companies Data: {SUBJECT}")
    BOOTSTRAP_SERVERS=Variable.get("Bootstrap-Servers")
    logger.info("-&-"*25)
    logger.info(f"Kafka Brokers : {BOOTSTRAP_SERVERS}")
    SCHEMA_REGISTRY_URL=Variable.get("Schema-Registry")
    logger.info("-^-"*25)
    logger.info(f"Schema Registry URL : {SCHEMA_REGISTRY_URL}")
    errors=0
    try : 
        ti = kwargs['ti']
        company_list = ti.xcom_pull( task_ids="etl_mabna_get_companies_req")
        logger.info(f"Len of Input data (Companies) : {len(company_list)}")
        logger.info("^-"*25)
        logger.info(f"First Entry : {company_list[0]}")
        logger.info(f"Last Entry : {company_list[-1]}")
        logger.info("^-"*25)
        schema_config = {"url" : f"{SCHEMA_REGISTRY_URL}" }
        logger.info(f"Schema Config : {schema_config}")
        logger.info("^-"*25)

        client= CachedSchemaRegistryClient(schema_config)    
        schema_id, schema, version = client.get_latest_schema(f"{SUBJECT}")
        if schema_id is None : 
            raise KafkaSchemaNotFound("Kafka Schema Not Found",SUBJECT)
        logger.info(f"Schema ID: {schema_id}, Schema : {schema}, Version : {version}")
        logger.info("*-"*25)
        i =1
        avroProducer = AvroProducer({
                'bootstrap.servers': f'{BOOTSTRAP_SERVERS}',
                'on_delivery': delivery_report,
                'schema.registry.url': f'{SCHEMA_REGISTRY_URL}'
                },
                default_value_schema=schema, default_key_schema=key_schema)
        com_cnt = 1
        for company in company_list : 
            try :
                logger.info(f"# {com_cnt:5} : {company['short_name']}")
                com_cnt +=1
                avroProducer.produce(topic=f'{TOPIC}', value=company, key = {'id' : company['id']})
                # logger.info(i)
                i+=1
                if (i%10==0) :
                    avroProducer.flush()
            except Exception as err : 
                clientAPM.capture_exception()
                logger.error(err)
                logger.error(f"Company Data :{company}")
                # clientAPM.capture_message("Company Info Errors")
                errors+=1

        avroProducer.flush()
        logger.info("%_"*25)
        logger.info(f"Number of Errors : {errors}")
        logger.info(f"Number of Records : {len(company_list)}")
        logger.info(f"Number of Inserted Records : {len(company_list) - errors}")
        logger.info("%_"*25)
        return True
    except Exception as e:
        logger.error("Exception: " + str(e))
        clientAPM.capture_exception()
        raise e

##----------------------------- Functions Ends Here---------------------------


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}
with DAG(
    'ETL-Mabna-Companies-2-Kafka',
    default_args=default_args,
    description='A simple HttpRequest DAG',
    schedule_interval=timedelta(days=30),
    start_date=days_ago(0),
    tags=['mabna', 'rest-api','ref-tables'],
) as dag:

    task_get_request = PythonOperator(
        task_id='etl_mabna_get_companies_req',
        python_callable=get_companies,
        dag=dag,
    )


    task_save_results = PythonOperator(
        task_id='etl_mabna_companies_to_kafka',
        python_callable=produce_companies,
        dag=dag,
    )

    task_trigger_processing = TriggerDagRunOperator( 
        task_id='etl_maba_companies_trigger_Kafka_2_PG',
        trigger_dag_id='ETL-Mabna-Companies-2-PG',
        conf={"message": "Hello World"},
    )

    task_get_request >> task_save_results >> task_trigger_processing