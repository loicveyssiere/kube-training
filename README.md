# MarkItDown — Distributed Processing Application

This project is a small distributed system composed of three services:

- **Redis** — in-memory datastore used as a message broker  
- **API** — HTTP server receiving tasks and managing uploads  
- **Worker** — background processor that consumes tasks from Redis  

All components are orchestrated using **Docker Compose**.

## 🚀 Architecture Overview

```
           +-----------+
           |   Redis   |
           |   6379    |
           +-----+-----+
                 ^
                 |
        +--------+---------+
        |                  |
 +------+-------+   +------+-------+
 |     API      |   |    Worker    |
 | Port 8000    |   | No exposed   |
 | Task ingest  |   | port         |
 +--------------+   +---------------+
```

## 📦 Services

### 1. Redis

Simple Redis instance exposed on port **6379**.

```yaml
redis:
  image: redis:7.4
  ports:
    - "6379:6379"
  restart: always
```

### 2. API

The HTTP API:

- receives tasks  
- handles file uploads  
- stores outputs  
- interacts with Redis  

Environment variables:

- REDIS_URL=redis://redis:6379/0
- UPLOAD_DIR=/data/uploads
- OUTPUT_DIR=/data/output
- TASK_STORE_FILE=/data/tasks.json

### 3. Worker

Background processor that:

- reads jobs from Redis  
- writes results in the output directory  

Environment variables:

- REDIS_URL=redis://redis:6379/0
- OUTPUT_DIR=/data/output

## ▶️ Running the Application

### Start all services
```
docker-compose up -d
```

### View logs
```
docker-compose logs -f api
docker-compose logs -f worker
```

### Stop everything
```
docker-compose down
```

## 📁 Project Structure

```
.
├── docker-compose.yml
├── server/
│   └── (API code)
├── worker/
│   └── (Worker code)
└── data/
    └── (runtime shared directory)
```

## ⚙️ Environment Variables

| Variable        | Used By     | Description                        |
|-----------------|-------------|------------------------------------|
| REDIS_URL       | API, Worker | Redis connection string            |
| UPLOAD_DIR      | API         | Directory for file uploads         |
| OUTPUT_DIR      | API, Worker | Directory for generated output     |
| TASK_STORE_FILE | API         | Path to task registry JSON file    |

## 🧪 Testing the API

Once started:
```
http://localhost:8000/
```

## 🛠️ Development Tips

- Use `docker exec -it <container> sh` to inspect running containers.
- Mount project directories via volumes for live code reload.
- Redis CLI:
```
docker exec -it redis redis-cli
```
