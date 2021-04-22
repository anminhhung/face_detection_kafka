from kafka import KafkaConsumer
import config as cfg
import json 

if __name__ == "__main__":
    draw_topic = cfg.draw_topic

    consumer = KafkaConsumer(
        draw_topic, 
        bootstrap_servers=['localhost:9092'])

    for msg in consumer:
        data = json.loads(msg.value)
        image_path = data["image_path"]

        print("image_path: ", image_path)