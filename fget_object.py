import psycopg2
from datetime import datetime,date
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from kafka import KafkaProducer
import os
import shutil
from minio import Minio
from glob_var import Const
import io
var = Const()
conn = psycopg2.connect(host    =   var.DB_HOST, 
                        database=   var.DB_NAME, 
                        user    =   var.DB_USER, 
                        password=   var.DB_PASS,
                        port    =   var.DB_PORT)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
c = conn.cursor()

# kafka_broker    = var.KAFKA_BROKER
# topic_event     = var.TOPIC_EVENT
# topic_ppe       = var.TOPIC_PPE
# producer        = KafkaProducer(bootstrap_servers=kafka_broker)

minio_address   = var.MINIO_ADDRESS
minio_address1  = 'minio.congtrinhviettel.com.vn'
bucket_name     = var.BUCKET_NAME
client          = Minio(
                        minio_address,
                        access_key=var.ACCESS_KEY,
                        secret_key=var.SECRET_KEY,
                        secure=False  # check ssl
                        )
today = date.today()
date = today.strftime("%b-%d-%Y")
# embedding_name = 'FACE/' + 'data_' + str(date)+ '/index.bin'
embedding_name = 'FACE/data_Nov-08-2022/index.bin'
client.fget_object(bucket_name=bucket_name,object_name =embedding_name ,file_path=os.getcwd()+"/index_pull.bin")

print("+++++++++++++++++++Push_object-++++++++++++++++++")