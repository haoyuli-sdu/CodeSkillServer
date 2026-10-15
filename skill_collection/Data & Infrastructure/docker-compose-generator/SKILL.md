---
name: "docker-compose-generator"
description: "Generate Docker Compose configurations for development environments - auto-detect project stack, configure services with dependencies, volumes, networking, and health checks"
---

# Docker Compose Generator

Generate production-ready Docker Compose configurations.

## Usage

```
/docker-compose-generator generate "<stack description>"
/docker-compose-generator add-service <service-name>
/docker-compose-generator validate [file]
/docker-compose-generator template <template-name>
```

## Supported Services

| Service | Image | Default Port |
| --- | --- | --- |
| PostgreSQL | postgres:16-alpine | 5432 |
| MySQL | mysql:8 | 3306 |
| Redis | redis:7-alpine | 6379 |
| MongoDB | mongo:7 | 27017 |
| Elasticsearch | elasticsearch:8 | 9200 |
| RabbitMQ | rabbitmq:3-management | 5672/15672 |
| Nginx | nginx:alpine | 80/443 |
| Qdrant | qdrant/qdrant | 6333 |
| Ollama | ollama/ollama | 11434 |
| MinIO | minio/minio | 9000/9001 |

## Templates

`fullstack` `microservice` `data-pipeline` `ml-stack` `monitoring`
