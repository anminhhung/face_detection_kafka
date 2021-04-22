import sys
import time
import cv2
import signal
import imutils
from kafka import KafkaProducer
import config as cfg
import json
from face_detect import detect_face_ssd
import numpy as np
import base64

def ConvertJsonType(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, datetime.datetime):
            return obj.__str__()

def publish_video(producer,topic,video_file="result.mov"):
    """
    Publish given video file to a specified Kafka topic. 
    Kafka Server is expected to be running on the localhost. Not partitioned.
    """
    # Open file
    video = cv2.VideoCapture(video_file)
    print('publishing video...')
    while(video.isOpened()):
        success, frame = video.read()
        frame = imutils.resize(frame,width=720)
        # Ensure file was read successfully
        if not success:
            print("bad read!")
            break
        # Convert image to png
        ret, buffer = cv2.imencode('.jpg', frame)
        # Convert to bytes and send to kafka
        producer.send(topic, buffer.tobytes())
        time.sleep(0.2)
    video.release()
    print('publish complete')

    
def publish_camera(producer,topic):
    camera = cv2.VideoCapture(0)
    while(True):
        try:
            success, frame = camera.read()

            if not success:
                print("bad read!")
                break
            frame = imutils.resize(frame,width=720)

            start_time = time.time()
            list_faces, list_scores, list_classes = detect_face_ssd(frame, NET_DNN)
            print("FPS: ", 1.0/(time.time() - start_time))

            # encode image
            _, buffer = cv2.imencode('.jpg', frame)
            encodedJPG = base64.b64encode(buffer).decode('utf-8')

            # write json
            info_json_dict = {
                "image": encodedJPG,
                "list_faces": list_faces,
                "list_scores": list_scores,
                "list_classes": list_classes
            }
            info_face_json = json.dumps(info_json_dict, default=ConvertJsonType)

            print("info_face_json box: ", info_json_dict["list_faces"])
   
            producer.send(topic, value=info_face_json)

        except KeyboardInterrupt:
            break
        except:
            continue

    producer.flush()
    camera.release()
    print('publish complete')

if __name__ == "__main__":
    topic = cfg.detect_topic

    """
    linger_ms
    1000ms --> 1sec
    100ms  --> 0.1sec
    """
    producer = KafkaProducer(bootstrap_servers='localhost:9092',
                        batch_size=15728640,
                        linger_ms=100,
                        max_request_size=15728640,
                        value_serializer=lambda v: v.encode('utf-8')
                        )

    PROTOTXT = "models/deploy.prototxt.txt"
    MODEL = "models/res10_300x300_ssd_iter_140000.caffemodel"
    NET_DNN = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)

    input_type = "webcam"
    if input_type == "video":
        print("sending frames...")
        publish_video(producer,topic)
    elif input_type == "webcam":
        print("sending frames...")
        publish_camera(producer,topic)