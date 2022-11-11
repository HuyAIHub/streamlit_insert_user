# # def check_id(file_path,id):
# #     f = open(file_path, "r")
# #     temp = f.read().splitlines()
# #     print(temp)
# #     if id in temp:
# #         return False
# #     return True
# # print(check_id('id.txt','428950'))
# import os
# path_route = '/home/ha/Desktop/streamlit_insert_user/Image_out/'
# Name = 'huydq41'
# if os.path.exists(path_route + Name):
#     os.rmdir(path_route + Name)
#     os.mkdir(path_route + Name)
# else:
#     os.mkdir(path_route + Name)

# def get_Area(box):
#     return (box[2] - box[0]) * (box[3] - box[1])
# main_box = [[621.0, 888.0, 1357.0, 1875.0], [1592.0, 1278.0, 1640.0, 1358.0]]
# bbox = [621.0, 888.0, 1357.0, 1875.0]
# bbox1 = [1592.0, 1278.0, 1640.0, 1358.0]
# # print('bbox:',get_Area(bbox))
# # print('bbox:',get_Area(bbox1))
# for i in range(len(main_box)):
#     max_box = main_box[0]
#     print(get_Area(max_box))
#     print(get_Area(main_box[i]))
#     if get_Area(max_box) >  get_Area(main_box[i]):
#         max_box = main_box[i]
# print('max_box:',max_box)
# import subprocess
# import sys,os
# os.chdir('module/yolov5-face')
# root = os.path.dirname(os.path.abspath(__file__))
# print(root)
# subprocess.call('pwd',shell=True)
# subprocess.Popen([sys.executable,'/data/huydq46/Face/streamlit_insert_user/module/yolov5-face/index_embedding.py'])

from glob_var import Const , db_connect, kafka_connect, minio_connect
from datetime import datetime,date
import os
minio_address, minio_address1, bucket_name, client = minio_connect()

today = date.today()
date = today.strftime("%b-%d-%Y")
embedding_name = 'FACE/' + 'data_' + str(date)+ '/index.bin' 
image_url = f'https://{minio_address1}/{bucket_name}/{embedding_name}'
client.fput_object(
        bucket_name = bucket_name, object_name = embedding_name, file_path= os.getcwd() + "/Datasets/index.bin",content_type='file/bin'
    )
print("+++++++++++++++++++Push_object-++++++++++++++++++")