from PIL import Image
import cv2
import streamlit as st
import numpy as np
# from deta import Deta
import psycopg2
from datetime import datetime,date
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
# from kafka import KafkaProducer
import os,sys
import shutil
from minio import Minio
from glob_var import Const , db_connect, kafka_connect, minio_connect
import subprocess
sys.path.append(os.getcwd()+'/module/yolov5-face')
from face_process import Processing_face

minio_address, minio_address1, bucket_name, client = minio_connect()

def push_index():
    embedding_name = 'FACE/' + 'data_'+ '/index.bin' 
    client.fput_object(
            bucket_name = bucket_name, object_name = embedding_name, file_path= os.getcwd() + "/Datasets/index.bin",content_type='file/bin'
        )
    print("+++++++++++++++++++Push_index_done!-++++++++++++++++++")
def check_id(file_path,id):
    f = open(file_path, "r")
    temp = f.read().splitlines()
    # print(temp)
    if id in temp:
        return True
    return False
def upload(name,List_object,types=['jpg', 'png', 'jpeg']):
    img_file_buffer = st.file_uploader(name, types)
    if img_file_buffer is not None:
        image = np.array(Image.open(img_file_buffer))
        List_object.append(image)
def main():
    List_object = []
    List_name = ["Upload chinh dien","Upload nghieng trai","Upload nghieng phai","Upload tren nhin xuong"]
    st.title("Mau Dang Ky Nhan Dien Khuon Mat")
    with st.form(key='my_form',clear_on_submit = True):
        path_route = os.getcwd() + '/Datasets/CNTT/'
        Name = st.text_input(label='Nhap ten mail vietel')
        print('Name:',Name)
        id_number = st.text_input(label='Nhap ma nhan vien')
        registered_at = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("## Nhap anh")
        for name in List_name:
            upload(name,List_object)
        submit_button = st.form_submit_button(label='Submit')
        if submit_button:
            if Name == '' or id_number == '' or len(List_object) != 4:
                new_title = '<p style="font-family:sans-serif; color:Red; font-size: 42px;">ban chua nhap du thong tin</p>'
                st.write(new_title, unsafe_allow_html=True)
                return

            if check_id(os.getcwd()+'/Datasets/id.txt',str(id_number)):
                if os.path.exists(path_route + Name):
                    shutil.rmtree(path_route + Name)
                    os.mkdir(path_route + Name)
                else:
                    os.mkdir(path_route + Name)
                for i,image in enumerate(List_object):
                    Processing_face(image,path_route + Name,i) # crop and align face after that save to folder embedding
                subprocess.Popen([sys.executable,'/data/huydq46/Face/streamlit_insert_user/module/yolov5-face/index_embedding.py'])
                # push_index()
            else:
                new_title = '<p style="font-family:sans-serif; color:Red; font-size: 42px;">MNV chua co trong CSDL</p>'
                st.write(new_title, unsafe_allow_html=True)
            st.write("submit done!")
            st.empty()
        
        List_object.clear()
if __name__ == '__main__':
    main()
