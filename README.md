# Start Zookeeper and kafka
To simplify the tedious task of building a kafka server, we will use Docker with Kafka and Zookeeper out of the box:
Go to the kafka-docker folder
<pre><code>$ cd kafka-docker </code></pre>

Start Kafka and Zookeeper with Docker Compose
<pre><code>$ docker-compose -f docker-compose_local.yml up </code></pre>

In the docker-compose_local.yml configuration file, the topics are defined, the url and the port through which our publisher and subscribers connected.

To stop Kafka uses
<pre><code>$ docker-compose stop </code></pre>
for more information Apache Kafka: Docker Container refer to this [post](https://towardsdatascience.com/kafka-docker-python-408baf0e1088)

# Demo 
## 1. Detect_producer
We will create a subsriber that take the webcame frames, detects face, encodes image and sends info to a topic named "detect_face".

```
    python3 detect_producer.py
```

## 2. Draw_producer
We create a subscriber that pulls the messages we store in the topic "detect_face" then draws bboxs, stores image and sends image path to a topic named "draw_face".

```
    python3 draw_producer.py
```

## 3. Get image path
We create a subscriber that pulls the messages we store in the topic "draw_face" then prints it.

```
    python3 read_path_consumer.py
```