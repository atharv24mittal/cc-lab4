# Docker Advanced Lab

## Features
- RabbitMQ message broker
- Two chat clients (user-a, user-b)
- Docker networks for communication
- Docker Compose orchestration
- Docker volumes for persistent chat history

## Run

### Start RabbitMQ
docker compose up rabbitmq

### Run users
docker compose run --rm user-a
docker compose run --rm user-b

## Concepts Learned
- Container networking
- Message queues
- Docker Compose
- Volumes (data persistence)
