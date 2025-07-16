# J-AIE-test
# FastAPI Application API

This repository houses the backend API for a FastAPI application, designed to manage knowledge, facilitate chat interactions, and provide comprehensive audit and action logging.

---

## Table of Contents

- [Features](#features)
- [API Endpoints](#api-endpoints)
  - [Knowledge Management](#knowledge-management)
  - [Chat Interactions](#chat-interactions)
  - [Audit Logging](#audit-logging)
  - [Action Log Management](#action-log-management)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Setup (Without Docker)](#local-setup-without-docker)
  - [Docker Setup](#docker-setup)
  - [Environment Variables (.env.deploy)](#environment-variables-envdeploy)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Features

This API offers a robust set of features, providing a complete solution for content management, interactive AI, and detailed operational insights:

* **Knowledge Management:**
    * **Create and Update Knowledge:** Seamlessly add new knowledge documents or update existing ones using a unique ID.
    * **Retrieve Knowledge:** Fetch all stored knowledge documents or get specific details for a document by its ID.
    * **Delete Knowledge:** Efficiently remove knowledge documents from the system.
    * **File Upload with Processing:** Upload various file types (`.pdf`, `.md`, `.txt`). The API automatically handles **chunking** and **embedding** these files into a vector database, making them ready for intelligent search and retrieval.
* **Real-time Chat:**
    * **Interactive Chat Stream:** Engage in dynamic, real-time chat sessions. The `enable_reasoning` option allows for more sophisticated and context-aware AI responses.
* **Audit Logging:**
    * **Retrieve Audit Logs:** Access detailed logs of all AI interactions, complete with pagination for easy navigation.
    * **Get Audit by ID:** Quickly retrieve a specific audit log using its unique chat ID.
* **Action Log Management:**
    * **Get All Action Logs:** Pull all system action logs. You can refine your search with **pagination** and filters for `action_type` (e.g., `chat`, `upsert`), `resource_type`, and `status` (`success`, `failed`, `other`).
    * **Get Log by ID:** Retrieve a single, specific action log record by its ID for detailed inspection.

---

## API Endpoints

This section details the available API endpoints, their methods, and expected behavior.

### Knowledge Management

| Method | Endpoint                    | Summary            | Description                                                                                                                                                                                                                                 |
| :----- | :-------------------------- | :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `POST` | `/knowledge/update`         | **Update Knowledge** | Creates a new knowledge document or updates an existing one if the `id` is provided. <br/> **Example for Create:** `[{"id": "uuid1", "text": "abc"}]` <br/> **Example for Update:** `[{"id": "uuid1", "text": "xyz"}]`                                    |
| `DELETE` | `/knowledge/{doc_id}`       | **Delete Knowledge** | Deletes a knowledge document by its unique `doc_id`.                                                                                                                                                                                      |
| `GET`  | `/knowledge`                | **Get Knowledge** | Retrieves all available knowledge documents.                                                                                                                                                                                              |
| `GET`  | `/knowledge/{knowledge_id}` | **Get Knowledge By Id**| Retrieves a specific knowledge document by its unique `knowledge_id`.                                                                                                                                                                   |
| `POST` | `/knowledge/upload`         | **Upload File** | Uploads a file for chunking and embedding into the vector database. Supported file types: `.pdf`, `.md`, `.txt`. <br/> **Request Body:** `multipart/form-data` with a `file` field.                                                          |

### Chat Interactions

| Method | Endpoint | Summary     | Description                                                                                             |
| :----- | :------- | :---------- | :------------------------------------------------------------------------------------------------------ |
| `POST` | `/chat`  | **Chat Stream** | Initiates a real-time chat session. <br/> **Example Input:** `{"text": "Tell me about AI", "enable_reasoning": true(default=false)}` |

### Audit Logging

| Method | Endpoint            | Summary                | Description                                                                                                        |
| :----- | :------------------ | :--------------------- | :----------------------------------------------------------------------------------------------------------------- |
| `GET`  | `/audit/{chat_id}`  | **Get Audit By Id Route** | Retrieves a specific audit log by its unique `chat_id`. <br/> **Example:** `/audit/your-chat-id-here`              |
| `GET`  | `/audit/`           | **Get All Audits** | Retrieves all logs related to AI interactions with pagination. <br/> **Example:** `/audit?skip=0&limit=20`        |

### Action Log Management

| Method | Endpoint          | Summary         | Description                                                                                                                                                                                             |
| :----- | :---------------- | :-------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GET`  | `/logs/`          | **Get All Logs** | Retrieves all system action logs with pagination and optional filters. <br/> **Parameters:** `skip`, `limit`, `action_type`, `resource_type`, `status`. <br/> **Example:** `/logs?skip=0&limit=20&action_type=chat` |
| `GET`  | `/logs/{log_id}`  | **Get Log By Id** | Retrieves a single action log by its unique `log_id`. <br/> **Example:** `/logs/your-log-id-here`                                                                                                      |

---

## Getting Started

You can set up and run this FastAPI application either directly on your local machine or using Docker for a containerized environment.

### Prerequisites
* **Docker** and **Docker Compose** (if using Docker setup)

### Docker Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```
2.  **Create your `.env.deploy` file:** See the [Environment Variables](#environment-variables-envdeploy) section below.
3.  **Build and run the Docker containers:**
    ```bash
    docker compose up --build
    ```
    This command will:
    * Build the Docker images defined in your `docker-compose.yml` (e.g., for the FastAPI app and PostgreSQL database).
    * Start the services. The FastAPI application will typically be accessible on `http://localhost:8000` (or `http://127.0.0.1:8000`) on your host machine, assuming port 8000 is mapped in your `docker-compose.yml`.

---

# Test API Access

You can test API access and explore the endpoints via the interactive documentation at `http://0.0.0.0:8000/docs` after starting the server.

---

### Chat with `curl` Commands

Here are some `curl` commands to quickly test the chat functionality:

**Chat without reasoning (default behavior)**

```bash
curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"text": "Tell me about AI"}'
```
**Chat with reasoning (default behavior)**

```bash
curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"text": "Tell me about AI", "enable_reasoning": true}'
```

### Environment Variables (.env.deploy)

Before running the application (either locally or with Docker), you must create a file named `.env.deploy` in the root directory of your project. This file will store sensitive information and configuration parameters.

```env
# Key
GOOGLE_API_KEY=AIzaSyA0LoRm4kFnv87sfRsJJCU80wq3qL5i74E # Replace or use free mine

# Model Name
EMBEDDING_MODEL_NAME=gemini-embedding-exp-03-07 # Google's experimental embedding model
LLM_MODEL_NAME=gemini-2.0-flash                 # Google's fast and efficient LLM

# Model Config
MODEL_TEMPERATURE=0.1   # Controls randomness in LLM output (0.0-1.0)
EMBEDDING_DIM=768       # Dimension of the embeddings
TOP_K=5                 # Number of top similar results to retrieve for RAG
MIN_SIM_SCORE=0.3       # Minimum similarity score for retrieved knowledge
MAX_OUTPUT_TOKEN=512    # Maximum tokens in LLM output

# Database Config
DB_URL=postgresql+asyncpg://user:pass@db:5432/vectordb # PostgreSQL connection string
PGVECTOR_LISTS=100      # Parameter for PGVector indexing (IVFFlat) - impacts search speed vs accuracy
CHUNK_SIZE=500          # Size of text chunks for embedding
CHUNK_OVERLAP=100       # Overlap between text chunks

# Other
PYTHONPATH=.            # Ensures Python can find modules within the project