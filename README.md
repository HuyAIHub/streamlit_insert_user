# Real Time Face Recognition System

## References and research:
RTSP,frame,video,...

Face detection (YOLOV5-face):
- https://github.com/biubug6/Pytorch_Retinaface (no work)
- https://github.com/deepcam-cn/yolov5-face (prefer)

Face recognition (Arc Face-paddle):
- Guideline and explanation inference: https://github.com/littletomatodonkey/insight-face-paddle 
- Inference: https://github.com/deepinsight/insightface/blob/master/recognition/arcface_paddle/deploy/pdserving/README.md 

## Flow Overview:
- Step 1: Streaming 
- Step 2: Face Detection
	- face bounding box, lanmark
	- face align and crop : -> face aligned
- Step 3: Tracking
- Step 4: Face Recognition
	- face recognition 
- Step 5: Output processing

## DO:
### Server 1: 
- The first - front end : Insert face image (ảnh chụp mặt) and information từ web.
- The second - back end: Crop and align face after that save to FOLDER (to make embedding theo tên đã nhập)
- The third - back end: Create index.bin (file này dùng để lưu {label:embedded} sau sẽ load lên để compare cosine distance)
- The fourth - back end: push index.bin to Minio and Send message notify using kafka to Server Inference.
### Server 2: Ở đây sẽ chạy infer và trả về kết quả
- The last - back end: After receiving a message. update index.bin and keep running
https://github.com/Quanghuy99/Real_Time_Face_Recognition
