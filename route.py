"import tempfile
import time

import folium
import webbrowser
from PIL import Image

import cv2
import numpy as np
import streamlit as st
from deta import Deta
import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import uuid
from src.lp_recognition import E2E
from kafka import KafkaProducer
from kafka.errors import KafkaError



DB_host = '10.248.243.216'
# DB_host = '103.160.78.147'
DB_name = 'vcc_ai_events'
DB_user = 'postgres'
DB_pass = 'Vcc_postgres@2022'
DB_port = 5432

conn = psycopg2.connect(host=DB_host, database=DB_name, user=DB_user, password=DB_pass, port=DB_port)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
c = conn.cursor()

def sql_executor(query):
	c.execute(query)
	data = c.fetchall()
	return data[-11:-1]

def sql_insert(insert_scrip,insert_value):
    c.execute(insert_scrip,insert_value)
    conn.commit()

def center_enthandle(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy
@st.cache()
def image_resize(image,width=None,height=None,inter = cv2.INTER_AREA):
    dim = None
    (h,w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = width/float(w)
        dim = (int(w*r),height)
    else:
        r = width/float(w)
        dim = (width,int(h*r))
    #resize the image
    resize = cv2.resize(image,dim,interpolation=inter)
    return resize

class Map:
    def __init__(self, center, zoom_start, name):
        self.center = center
        self.zoom_start = zoom_start
        self.name = name

    def showMap(self,data):
        # Create the map
        my_map = folium.Map(location=self.center, zoom_start=self.zoom_start)
        for (index,row) in data.iterrows():
            folium.Marker(location=[row.loc['latitude'],row.loc['longitude']],popup = '<strong>'+row.loc['name']+'<\strong>').add_to(my_map)

        # Display the map
        my_map.save(""map.html"")
        webbrowser.open(""map.html"")

Insert_registered_camera = 'INSERT INTO vcc_events_management.camera(name, description, construction_id, streaming_url, latitude, Longitude, Coordinates) VALUES (%s, %s, %s, %s, %s, %s, %s)'
Insert_registered_user = 'INSERT INTO vcc_events_management.registered_user(name, company, contact_address, role, contact_number,registered_at,registered_by) VALUES (%s, %s, %s, %s, %s, %s, %s)'
Insert_registered_vehicle = 'INSERT INTO vcc_plr.registered_vehicle(type, description, owner_person, owner_company,registered_at,registered_by,updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)'
Insert_event = 'INSERT INTO vcc_plr.lpr (IP_cam, Time, Img_path_plate, Img_path_vehicle, LP_recog) VALUES (%s, %s, %s, %s,%s)'
Insert_event_vehicle = 'INSERT INTO vcc_events_management.vehicle_detection_event (vehicle_detect_direction, vehicle_detect_license_plate_number, vehicle_detect_type, vehicle_detect_is_stranger, vehicle_id, detail_id) VALUES (%s, %s, %s, %s, %s, %s)'

select_user = ""SELECT * FROM vcc_events_management.registered_user;""
select_vehicle = ""SELECT * FROM vcc_events_management.registered_vehicle;""
select_camera = ""SELECT * FROM vcc_events_management.camera;""
select = ""SELECT * FROM vcc_plr.lpr;""
select_event_vehicle = ""SELECT * FROM vcc_events_management.vehicle_detection_event;""

model = E2E()

video_demo = 'samples/video.MOV'
Plate_detect = ['Null']
detect = []
offset = 20  # allowable error between pixel
ip_cam = 'rtsp://tapoadmin:12345678a@172.18.6.57:554/stream1'
def main():
    menu = [""Register_user"", ""Register_vehicle"",""Register_camera"", ""Image_plate_recognize"", ""Streaming_plate_recognition"", ""Location_construction""]
    choice = st.sidebar.selectbox(""Menu"", menu)

    if choice == ""Register_user"":
        st.title(""Form Regrister User"")
        st.subheader(""It's quick and easy."")
        col1, col2 = st.columns(2)
        with col1:
            with st.form(key='my_form'):
                # ID = str(uuid.uuid4())
                Name = st.text_input(label='Enter your Name')
                Company = st.text_input(label='Enter your Company')
                Contact_address = st.text_input(label='Enter your Contact Address')
                Role = st.text_input(label='Enter your Role')
                Contact_number = st.text_input(label='Enter your Phone Number')
                registered_at = str(datetime.now().strftime(""%Y-%m-%d %H:%M:%S""))
                Registered_by = st.text_input(label='Enter your device')
                value_registered_user = (
                Name, Company, Contact_address, Role, Contact_number, registered_at, Registered_by)
                submit_button = st.form_submit_button(label='Submit',on_click=sql_insert(Insert_registered_user,value_registered_user))
                if submit_button:
                    st.write(""submit done!"")

        with col2:
            st.info(""info"")
            query_results = sql_executor(select_user)
            with st.expander(""Pretty Table""):
                query_df = pd.DataFrame(query_results)
                st.dataframe(query_df)
    elif choice == ""Register_vehicle"":
        st.title(""Form Regrister Vehicle"")
        st.subheader(""Register_vehicle"")
        col1, col2 = st.columns(2)
        with col1:
            with st.form(key='my_form'):
                # ID = str(uuid.uuid4())
                Type = st.text_input(label='Enter your Type vehicle')
                Description = st.text_input(label='Enter some info')
                Owner_person = st.text_input(label='Enter your ID number')
                Owner_company = st.text_input(label='Enter your Company')
                Registered_at = str(datetime.now().strftime(""%Y-%m-%d %H:%M:%S""))
                Registered_by = st.text_input(label='Enter your device')
                updated_at = str(datetime.now().strftime(""%Y-%m-%d %H:%M:%S""))
                value_registered_vehicle = (
                Type, Description, Owner_person, Owner_company, Registered_at, Registered_by, updated_at)
                submit_button = st.form_submit_button(label='Submit',on_click = sql_insert(Insert_registered_vehicle,value_registered_vehicle))
                if submit_button:
                    st.write(""submit done!"")

        with col2:
            st.info(""info"")
            query_results = sql_executor(select_vehicle)
            with st.expander(""Pretty Table""):
                query_df = pd.DataFrame(query_results)
                st.dataframe(query_df)
    elif choice == ""Register_camera"":
        st.title(""Form Regrister Cammera"")
        st.subheader(""Quick Start"")
        col1, col2 = st.columns(2)
        with col1:
            with st.form(key='my_form'):
                # ID = str(uuid.uuid4())
                Name = st.text_input(label='Enter your name of construction')
                Description = st.text_input(label='Enter some info')
                Construction_id = str(uuid.uuid4())
                Stream_url = st.text_input(label='Enter your url camera ip')
                Latitude = st.number_input('Enter your Latitude (vĩ độ)', format = ""%f"")
                Longitude = st.number_input('Enter your Longitude (kinh độ)',format = ""%f"")
                Coordinates = '{{638, 560}, {771, 482}, {882, 525}, {1054, 400}, {1476, 442}, {1781, 878}, {799, 887}}'# input tu thao
                value_registered_camera = (
                    Name, Description, Construction_id, Stream_url, float(Latitude), float(Longitude), Coordinates)
                submit_button = st.form_submit_button(label='Submit', on_click=sql_insert(Insert_registered_camera,value_registered_camera))
                if submit_button:
                    st.write(""submit done!"")

        with col2:
            st.info(""info"")
            query_results = sql_executor(select_camera)
            with st.expander(""Camera info table""):
                query_df = pd.DataFrame(query_results)
                st.dataframe(query_df)
    elif choice == ""Image_plate_recognize"":
        st.title(""Image Plate Recognition"")
        st.sidebar.markdown('---')
        col1, col2 = st.columns(2)
        with col1:
           pass
        with col2:
            pass
        st.markdown(""<hr/>"", unsafe_allow_html=True)
        img_file_buffer = st.file_uploader(""Upload an Image"", type=['jpg', 'png', 'jpeg'])
        if img_file_buffer is not None:
            image = np.array(Image.open(img_file_buffer))
        else:
            demo_image = 'samples/33.jpg'
            image = np.array(Image.open(demo_image))
        width = image.shape[1]
        height = image.shape[0]
        st.write(""Width"", width)
        st.write(""Height"", height)
        # start
        start = time.time()
        out_image = model.predict(image)
        # end
        end = time.time()
        st.write(""Time infer"", end - start)

        st.subheader(""Output Image"")
        st.image(out_image)
    elif choice == ""Streaming_plate_recognition"":
        st.set_option('deprecation.showfileUploaderEncoding',False)
        use_webcam = st.sidebar.button(""Use Webcam tại trung tâm"")
        use_webcam2 = st.sidebar.button(""Use Webcam ngoài 1"")
        use_webcam3 = st.sidebar.button(""Use Webcam ngoài 2"")
        use_webcam4 = st.sidebar.button(""Use Webcam ngoài 3"")
        record = st.sidebar.checkbox(""Record Video"")

        if record:
            st.checkbox(""Recording"",value=True)

        st.subheader(""License Plate Recognition"")
        st.sidebar.markdown('---')

        st.markdown(""## Output"")
        stframe = st.empty()
        video_file_buffer = st.sidebar.file_uploader(""Upload a Video"", type=['mp4','mov','avi','asf','m4v'])
        tffile = tempfile.NamedTemporaryFile(delete=False)
        if not video_file_buffer:
            if use_webcam:
                vid = cv2.VideoCapture(""rtsp://tapoadmin:12345678a@172.18.6.57:554/stream1"")
            elif use_webcam2:
                vid = cv2.VideoCapture(""rtsp://ubndtp:123456a@@cbg-svd.vddns.vn:554/av0_0"")
            elif use_webcam3:
                vid = cv2.VideoCapture(""rtsp://ubndtp:123456a@@cbg-ngatunacap.vddns.vn:554/av0_0"")
            elif use_webcam4:
                vid = cv2.VideoCapture(""rtsp://ubndtp:123456a@@cbg-ngatunacap.vddns.vn:555/av0_0"")
            else:
                vid = cv2.VideoCapture(video_demo)
        else:
            tffile.write(video_file_buffer.read())
            vid = cv2.VideoCapture(tffile.name)
        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        st.write(""height"",height)
        fps_input = int(vid.get(cv2.CAP_PROP_FPS))
        #recording part
        codec = cv2.VideoWriter_fourcc('M','J','P','G')
        out = cv2.VideoWriter('output1.mp4',codec,fps_input,(width,height))

        st.sidebar.text('Input Video')
        st.sidebar.video(tffile.name)
        fps = 0
        i = 0

        # with col2:
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.markdown(""Rate Fame"")
            kpi1_text = st.markdown(""0"")
        with kpi2:
            st.markdown(""License Plate"")
            kpi2_text = st.markdown(""0"")
        with kpi3:
            st.markdown(""width"")
            kpi3_text = st.markdown(""0"")
        st.markdown(""<hr/>"",unsafe_allow_html=True)
        capture_line_position = st.sidebar.slider('Rule line detection', min_value=0, max_value=height,
                                                  value=260, step=1)

        prevTime = 0
        while (vid.isOpened()):

            ret, frame1 = vid.read()
            width = frame1.shape[1]
            height = frame1.shape[0]
            if not ret:
                continue

            frame1.flags.writeable = True
            frame1 = cv2.resize(frame1, dsize=None, fx=0.5, fy=0.5)

            coor = model.LPextract(frame1)[0]  # toa do bien so
            # cv2.line(frame1, (20, capture_line_position), (width + height, capture_line_position), (0, 255, 0),
            #          2)  # set_rule_line
            for i in coor:
                X, Y, w, h = i[0], i[1], i[2], i[3]
                print(""x {} y {} w {} h {}"".format(X,Y,w,h))
                check = (w >= 35) and (h >= 35)
                if not check:
                    continue

                central_point_in_palte = (Y + h + Y) / 2
                # model.predict(frame1)
                if X < 0:
                    X = 0
                x, y = X, Y
                Plate_detect.append(model.format())
                # print(""license_plate: "",Plate_detect)

                center = center_handle(x, y, w, h)
                detect.append(center)
                #cv2.circle(frame1, center, 4, (0, 0, 255), -1)
                for (x, y) in detect:
                    # print(""Y {} x {} central_point_in_palte {}"".format(y,x, central_point_in_palte))
                    if central_point_in_palte < (capture_line_position + offset) and central_point_in_palte > (
                            capture_line_position - offset):
                        # img = model.predict(frame1)
                        model.predict(frame1)

                        img_path = '/home/huydq/PycharmProjects/LPR/License-Plate-Recognition/static/Img_vehicle/' + str(
                            Plate_detect[-1]) + "".png""
                        cv2.imwrite(img_path, frame1)

                        img_copy = frame1.copy()
                        crop = img_copy[Y: Y + h, X:X + w]  # cut license plate
                        img_plate = '/home/huydq/PycharmProjects/LPR/License-Plate-Recognition/static/Img_plate/' + str(
                            Plate_detect[-1]) + "".png""
                        cv2.imwrite(img_plate, crop)

                        # Insert_value = (None, Plate_detect[-1], None, )

                        Insert_value = (ip_cam, str(datetime.now().strftime(""%Y-%m-%d %H:%M:%S"")), img_plate, img_path, Plate_detect[-1])

                        sql_insert(Insert_event,Insert_value)
                        # sql_insert(Insert_event,Insert_value)
                        conn.commit()

                    # cv2.line(frame1, (20, capture_line_position), (width + height, capture_line_position),
                    #          (0, 127, 255),
                    #          2)  # set_rule_line
                    detect.remove((x, y))
                    # print(""license ..."", Plate_detect[-1])

            # cv2.putText(frame1, ""License is: "" + str(Plate_detect[-1]), (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 2,
            #             (157, 168, 50), 5)

            #FPS
            currTime = time.time()
            fps = round(1/(currTime - prevTime))
            prevTime = currTime

            if record:
                out.write(frame1)

            #Dashbord
            kpi1_text.write(f""<h1 style='text-align: center; color:red;'>{fps}</h1>"",unsafe_allow_html=True)
            kpi2_text.write(f""<h1 style='text-align: center; color:red;'>{Plate_detect[-1]}</h1>"", unsafe_allow_html=True)
            kpi3_text.write(f""<h1 style='text-align: center; color:red;'>{width}</h1>"", unsafe_allow_html=True)

            # frame1 = cv2.resize(frame1, dsize=None, fx=0.3, fy=0.3)
            frame1 = image_resize(image = frame1,width = 640)
            stframe.image(frame1,channels= 'BGR', use_column_width = True)

        st.text(""Video Processing"")
        out_putvideo = open('output1.mp4','rb')
        out_bytes = out_putvideo.read()
        st.video(out_bytes)
        vid.release()
        cv2.destroyAllWindows()

        st.markdown(""<hr/>"", unsafe_allow_html=True)
        st.info(""Event license plate"")
        query_results = sql_executor(select)
        with st.expander(""event""):
            query_df = pd.DataFrame(query_results)
            st.dataframe(query_df)


    else:
        query_for_map = ""SELECT name, latitude, longitude FROM vcc_events_management.camera WHERE latitude <> 0 AND longitude <> 0;""

        # data = {'name': [""Louis City Hoàng Mai"", ""Viettel Construction"", ""Viettel Đầu Tư Quốc Tế""],
        #         'latitude': [20.98224933889509, 21.01976443551583, 21.017077715065252],
        #         'longitude': [105.8590406643693, 105.78945039999999, 105.78419130611944]}
        # construction = pd.DataFrame(data=data)

        construction = sql_executor(query_for_map)
        construction = pd.DataFrame(data=construction).rename({0:'name',1:'latitude',2:'longitude'},axis='columns')

        map = Map(center=[20.98224933889509, 105.8590406643693], zoom_start=8, name='Louis City Hoàng Mai')
        map.showMap(construction)

if __name__ == '__main__':
    main()
"