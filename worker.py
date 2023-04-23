import pika
import os
import time
from os.path import join, dirname
from dotenv import load_dotenv
from openai_api import *
from whatsapp_api import *


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Define as configurações de conexão com o RabbitMQ
rabbitmq_host = os.environ['RABBITMQ_HOST']
rabbitmq_port = os.environ['RABBITMQ_PORT']
rabbitmq_user = os.environ['RABBITMQ_USER']
rabbitmq_pass = os.environ['RABBITMQ_PASS']
rabbitmq_queue = os.environ['RABBITMQ_QUEUE']
rabbitmq_return_queue = os.environ['RABBITMQ_RETURN_QUEUE']

# Conecta ao RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=rabbitmq_host, port=rabbitmq_port,
    credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)))
channel = connection.channel()

# Cria as filas, se elas não existirem
channel.queue_declare(queue=rabbitmq_queue)
channel.queue_declare(queue=rabbitmq_return_queue)

# Define a função para lidar com as mensagens da fila
def callback(ch, method, properties, body):
    print("Received message:", body)
    print(properties.correlation_id)
    corr_id = properties.correlation_id


    intention = classify_text(body.decode("utf-8"))
    print(intention)

    if intention == 'Criar uma imagem':
        try:
          dalle_msg = dalle_return(body.decode("utf-8"))
          message_returned = dalle_msg
        except:
          message_returned = 'ERROR'


    elif intention == 'Responder uma pergunta':
        try:
          prompt = (f"{body.decode('utf-8')}. Me responda apenas em português e de forma efetiva e direta")
          gpt_msg = gpt_return(prompt)
          message_returned = gpt_msg
        except:
          message_returned = 'ERROR'
    
    data = {
       "intention":intention,
       "message_returned":message_returned
    }

    # Publica a mensagem na fila de retorno
    channel.basic_publish(exchange='',
                          routing_key=rabbitmq_return_queue,
                            properties=pika.BasicProperties(correlation_id=corr_id),

                          body=str(data))
    
    print("Sent message to return queue:", str(data))

# Começa a consumir mensagens da fila
channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)

# Aguarda as mensagens
print('Waiting for messages...')
channel.start_consuming()
