import numpy as np 
import cv2 
from kafka import KafkaConsumer, KafkaProducer
import json 
import os
import config as cfg
import base64
import time 
from time import gmtime, strftime

def draw_bbox(m):
    image = m[0]
    boxes_face = m[1]
    for box in boxes_face:
        image = cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 2)

    return image

def ConvertJsonType(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, datetime.datetime):
            return obj.__str__()

def draw_process(producer, topic, consumer, dest_dir):
    for msg in consumer:
        data = json.loads(msg.value)
        list_boxes = data['list_faces']

        # decode image
        image_encode = data["image"]
        image_decode = base64.b64decode(image_encode)
        arr_image = np.fromstring(image_decode, np.uint8)
        image = cv2.imdecode(arr_image, cv2.IMREAD_COLOR)

        image_name = strftime("%Y_%m_%d_%H_%M_%S", gmtime()) + '.jpg'
        image_path = os.path.join(dest_dir, image_name)

        for bbox in list_boxes:
            # draw reg
            image = cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 2)

            # save image
            cv2.imwrite(image_path, image)
        
        print("image_path: ", image_path)
        output_dict = {"image_path": image_path}
        # write json
        output_json = json.dumps(output_dict, default=ConvertJsonType)

        # send producer
        producer.send(topic, value=output_json)

        producer.flush()
    
    print('publish complete')

if __name__ == "__main__":
    producer = KafkaProducer(bootstrap_servers='localhost:9092',
                        batch_size=15728640,
                        linger_ms=100,
                        max_request_size=15728640,
                        value_serializer=lambda v: v.encode('utf-8')
                        )

    detect_topic = cfg.detect_topic
    draw_topic = cfg.draw_topic

    consumer = KafkaConsumer(
        detect_topic, 
        bootstrap_servers=['localhost:9092'])

    dest_dir = "images"
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    draw_process(producer, draw_topic, consumer, dest_dir)