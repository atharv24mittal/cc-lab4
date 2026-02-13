import pika
import threading
import os
import time
import sys
import json

RABBIT_HOST = os.getenv('RABBIT_HOST', 'localhost')
QUEUE_NAME = os.getenv('QUEUE_NAME', 'chat_queue')
TARGET_QUEUE = os.getenv('TARGET_QUEUE')
USER_NAME = os.getenv('USER_NAME', 'unknown-user')
HISTORY_FILE = "/app/data/history.txt"
STANDALONE_MODE = os.getenv('STANDALONE_MODE', 'false').lower() == 'true'

os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)


def save_to_history(message):
    with open(HISTORY_FILE, "a") as f:
        f.write(message + "\n")


def display_history():
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
        print("\n--- Chat History ---")
        with open(HISTORY_FILE, "r") as f:
            print(f.read(), end="")
        print("--- End of History ---\n")
    else:
        print("\n--- No Previous Chat History ---\n")


def callback(ch, method, properties, body):
    try:
        data = json.loads(body.decode())
        sender = data.get("sender", "unknown")
        message = data.get("message", "")

        log = f"Received from {sender}: {message}"
        print(f"\n{log}\nType message: ", end="", flush=True)
        save_to_history(log)

    except Exception as e:
        print("Error decoding message:", e)


def get_connection():
    for i in range(5):
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBIT_HOST)
            )
        except:
            print(f"RabbitMQ not ready, retrying... ({i+1}/5)")
            time.sleep(2)

    print(f"\nERROR: Could not connect to RabbitMQ at {RABBIT_HOST}")
    return None


def listen():
    connection = get_connection()
    if not connection:
        return

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(queue=QUEUE_NAME,
                          on_message_callback=callback,
                          auto_ack=True)
    channel.start_consuming()


if STANDALONE_MODE:
    print("Standalone mode")
    sys.exit(0)

display_history()

threading.Thread(target=listen, daemon=True).start()

print(f"--- Chat Started ({USER_NAME} connecting to {RABBIT_HOST}) ---")

connection = get_connection()
if not connection:
    sys.exit(1)

channel = connection.channel()
channel.queue_declare(queue=TARGET_QUEUE)

try:
    while True:
        text = input("Type message: ")
        if text.strip():
            payload = {
                "sender": USER_NAME,
                "message": text
            }

            channel.basic_publish(
                exchange='',
                routing_key=TARGET_QUEUE,
                body=json.dumps(payload)
            )

            log = f"Sent by {USER_NAME}: {text}"
            print(log)
            save_to_history(log)

except KeyboardInterrupt:
    connection.close()
    print("\nChat ended.")
