from PIL import Image
import cv2
import streamlit as st
import numpy as np
import pandas as pd
# from deta import Deta
import psycopg2
from datetime import datetime,date,time,timedelta
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
conn, cur  = db_connect()

def Push_database(Name,id_number):
    current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    Insert_event = 'INSERT INTO face_recognition.employee(employee_id, name, created_date) VALUES (%s, %s, %s)'
    insert_value = (id_number,Name,current_time)
    cur.execute(Insert_event, insert_value)
    conn.commit()

def sql_executor(query):
	cur.execute(query)
	data = cur.fetchall()
	return data
    
def push_index():
    embedding_name = 'FACE/' + 'data_'+ '/index.bin' 
    client.fput_object(
            bucket_name = bucket_name, object_name = embedding_name, file_path= os.getcwd() + "/Datasets/index.bin",content_type='file/bin'
        )
    print("+++++++++++++++++++Push_index_done!-++++++++++++++++++")
def check_id(file_path,id):
    '''to check people exist'''
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

def input_people():
    List_object = []
    List_name = ["Ảnh chính diện","Ảnh nghiêng trái","Ảnh nghiêng phải","Ảnh nhìn xuống","Ảnh nhìn lên"]
    st.markdown("<h1 style='text-align: center; color: Red;'>MẪU ĐĂNG KÝ NHẬN DIỆN KHUÔN MẶT TẠI VCC</h1>", unsafe_allow_html=True)
    # st.title("VCC-AI-FACERECOGNITION")
    with st.form(key='my_form',clear_on_submit = True):
        path_route = os.getcwd() + '/Datasets/CNTT/'
        Name = st.text_input(label='Nhập Tên Mail Viettel:').lower()
        print('Name:',Name)
        id_number = st.text_input(label='Nhập Mã Nhân Viên:')
        # registered_at = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: Red;'>Nhập Ảnh</h3>", unsafe_allow_html=True)
        
        for name in List_name:
            upload(name,List_object)
        submit_button = st.form_submit_button(label='Submit!')
        if submit_button:
            if Name == '' or id_number == '' or len(List_object) != len(List_name):
                new_title = '<p style="font-family:sans-serif; color:Red; font-size: 42px;">Bạn chưa nhập đủ thông tin!</p>'
                st.write(new_title, unsafe_allow_html=True)
                return

            if check_id(os.getcwd()+'/Datasets/id.txt',str(id_number)):
                
                if os.path.exists(path_route + Name):
                    shutil.rmtree(path_route + Name)
                    os.mkdir(path_route + Name)
                else:
                    Push_database(Name,id_number) # bắn vào bảng nhân viên nếu chưa có
                    os.mkdir(path_route + Name)
                for i,image in enumerate(List_object):
                    Processing_face(image,path_route + Name,i) # crop and align face after that save to folder embedding
                subprocess.Popen([sys.executable,'/data/huydq46/Face/streamlit_insert_user/module/yolov5-face/index_embedding.py'])
                # push_index()
            else:
                new_title = '<p style="font-family:sans-serif; color:Red; font-size: 42px;">MNV chưa có trong CSDL</p>'
                st.write(new_title, unsafe_allow_html=True)
            title_done = '<p style="font-family:sans-serif; color:Green; font-size: 42px;">Bạn đã nhập thành công!</p>'
            st.write(title_done, unsafe_allow_html=True)
            st.empty()
        
        List_object.clear()
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def extract_time():
    start = "07:30"
    end = "08:30"
    times = []
    start = now = datetime.strptime(start, "%H:%M")
    end = datetime.strptime(end, "%H:%M")
    while now != end:
        times.append(str(now.strftime("%H:%M")))
        now += timedelta(minutes = 1)
    times.append(end.strftime("%H:%M"))
    return times

def Manament_day():
    st.markdown("<h1 style='text-align: center; color: Red;'>QUẢN LÝ CHẤM CÔNG NGÀY</h1>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: Red;'>Kiểm Tra Chấm Công Theo Ngày</h3>", unsafe_allow_html=True)
    d = st.date_input("chọn ngày")
    print('d:',d)
    select_user = 'WITH cte_table AS(SELECT name,employee_id,MIN (time_check) as time_check FROM face_recognition.vcc_face_event WHERE (CAST (time_check AS DATE) = \''+ str(d) +'\') AND name != \'' +'unknown'+ '\' \
        GROUP BY (name,employee_id))SELECT cte.name employee_id,cte.time_check,image_url FROM cte_table as cte INNER JOIN face_recognition.vcc_face_event using(time_check);'
    query_results = sql_executor(select_user)
    df = pd.DataFrame(query_results,columns=('Tên Nhân Viên','Thời Gian','Link Ảnh'))
    if st.button('Kiểm Tra'):
        with st.expander("Danh sách chấm công ngày: " + str(d)):
            st.dataframe(df)
            # st.dataframe(df)
            st.write('Số lượng người: '+str(len(df)))
            csv = convert_df(df)
            st.download_button(
            label="Tải dữ liệu!",
            data=csv,
            file_name='Dữ liệu chấm công ngày '+ str(d)+'.csv',
            mime='text/csv',)
    
    # # time filter
    # times = extract_time() #extract time into single minute
    # time_time = st.multiselect('Thời gian lọc:',times)
    # print('adâd:',time_time)
    # button = st.button('lọc',disabled=False)
    # if button :
    #     if len(time_time) <= 2:
    #         st.write(time_time)
    #     else:
    #         st.warning("You have to select only 2 locations")
    
    # show images
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: Red;'>Hiển Thị Ảnh</h3>", unsafe_allow_html=True)
    if st.button('Hiển Thị'):
        # st.header("Hình Ảnh")
        for i in range(len(df)):
            st.write(df['Tên Nhân Viên'][i] + ' vào lúc ' + str(df['Thời Gian'][i]))
            st.image(df['Link Ảnh'][i])
    
    st.markdown("<hr/>", unsafe_allow_html=True)
    
def Manament_month():
    st.markdown("<h1 style='text-align: center; color: Red;'>QUẢN LÝ CHẤM CÔNG THÁNG</h1>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: Red;'>Hãy Chọn Khoảng Thời Gian</h3>", unsafe_allow_html=True)
    start_date, end_date = st.date_input('Ngày bắt đầu:',datetime.today().replace(day=1)),st.date_input('Ngày kết thúc:')
    
    select_user = 'with cte_tables as(\
                        SELECT name, COUNT (CAST((time_check) AS DATE)) \
                        FROM face_recognition.vcc_face_event \
                        WHERE (CAST((time_check) AS DATE) BETWEEN \'' + str(start_date)+ '\' AND \'' + str(end_date)+ '\') AND name != \'' +'unknown'+ '\' \
                        GROUP BY (name,CAST((time_check) AS DATE))) \
                    SELECT name, COUNT(name) \
                    FROM cte_tables \
                    GROUP BY(name);'
    
    query_results = sql_executor(select_user)
    df = pd.DataFrame(query_results,columns=('Tên Nhân Viên','Số Ngày Làm Việc',))
    if st.button('Kiểm Tra'):
        if start_date < end_date:
            pass
        else:
            st.error('Lỗi: Ngày kết thúc phải sau ngày bắt đầu.')
                
        with st.expander("Danh sách chấm công tháng: "):
            st.dataframe(df)
            # st.dataframe(df)
            csv = convert_df(df)
            st.download_button(
            label="Tải dữ liệu!",
            data=csv,
            file_name='Dữ liệu chấm công tháng.csv',
            mime='text/csv',)

    st.markdown("<hr/>", unsafe_allow_html=True)
    
def main():
    menu = ['Khai Báo Nhân Viên','Kiểm Tra Chấm Công Ngày','Kiểm Tra Chấm Công Tháng']
    choice = st.sidebar.selectbox("Menu", menu)
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #0099ff;
        color:#ffffff;
    }
    div.stButton > button:hover {
        background-color: #00ff00;
        color:#ff0000;
        }
    </style>""", unsafe_allow_html=True)
    if choice == menu[0]:
        input_people()
    elif choice == menu[1]:
        Manament_day()
    elif choice == menu[2]:
        Manament_month()
        
if __name__ == '__main__':
    main()