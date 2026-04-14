# Synapse Research Agent

A FastAPI application that runs intelligent research agents asynchronously in the background.

## Features

- Asynchronous background task processing using `ThreadPoolExecutor`.
- Thread-safe in-memory task storage.
- Simple task status tracking (queued, running, completed, failed, cancelled).
- API for submitting, checking status, listing, and attempting to cancel tasks.
- CORS middleware enabled (configurable for production).
- Basic health check endpoint.
- OpenAPI documentation (/docs, /redoc).

## Setup

1.  **Clone Repository**
2.  **Create & Activate Virtual Environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  **Install Dependencies**
    ```bash
    pip install -e .
    ```
4.  **Environment Variables**
    Create a `.env` file in the project root with your `BRIGHT_DATA_API_TOKEN`:
    ```
    BRIGHT_DATA_API_TOKEN=your_api_token_here
    ```

## Running the API

```bash
python server.py
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### 1. Submit Research Task

-   **POST** `/research`
-   **Description**: Submits a new topic for research. The task is added to a queue and processed in the background.
-   **Request Body**:
    ```json
    {
      "topic": "Your research topic (min 3 chars)"
    }
    ```
-   **Response (202 Accepted)**:
    ```json
    {
      "task_id": "uuid-string-for-the-task",
      "status": "queued",
      "message": "Research task submitted and will be processed."
    }
    ```

### 2. Get Task Status

-   **GET** `/research/{task_id}`
-   **Description**: Retrieves the current status and details of a specific research task.
-   **Response (200 OK)**:
    ```json
    {
      "task_id": "uuid-string-for-the-task",
      "topic": "Your research topic",
      "status": "queued|running|completed|failed|cancelled|cancellation_requested",
      "created_at": "2023-10-27T10:00:00.000000",
      "result": "Research results if task is completed...",
      "error": "Error message if task failed...",
      "completed_at": "2023-10-27T10:05:00.000000", // If completed
      "failed_at": "2023-10-27T10:03:00.000000"    // If failed
    }
    ```
-   **Response (404 Not Found)**: If `task_id` does not exist.

### 3. List All Tasks

-   **GET** `/tasks`
-   **Description**: Retrieves a list of all submitted tasks. Can be filtered by status.
-   **Query Parameters**:
    -   `status` (optional): Filter by task status (e.g., `queued`, `running`, `completed`).
-   **Response (200 OK)**:
    ```json
    {
      "tasks": [
        {
          "task_id": "uuid-string-1",
          "topic": "Topic 1",
          "status": "completed",
          "created_at": "2023-10-27T09:00:00.000000",
          "completed_at": "2023-10-27T09:05:00.000000"
        },
        {
          "task_id": "uuid-string-2",
          "topic": "Topic 2",
          "status": "running",
          "created_at": "2023-10-27T10:00:00.000000",
          "completed_at": null
        }
      ],
      "total": 2
    }
    ```

### 4. Cancel Task

-   **DELETE** `/research/{task_id}`
-   **Description**: Attempts to mark a task for cancellation. If the task is already running, it might complete before cancellation takes effect (soft cancellation). Queued tasks are directly marked as cancelled.
-   **Response (200 OK)**:
    ```json
    {
        "task_id": "uuid-string-for-the-task",
        "status": "cancelled|cancellation_requested",
        "message": "Task cancellation processed."
    }
    ```
-   **Response (404 Not Found)**: If `task_id` does not exist.
-   **Response (409 Conflict)**: If task is already completed/failed and cannot be cancelled.

### 5. Health Check

-   **GET** `/health`
-   **Description**: A simple endpoint to check if the API is running.
-   **Response (200 OK)**:
    ```json
    {
      "status": "healthy",
      "timestamp": "2023-10-27T10:15:00.000000"
    }
    ```

## API Documentation

Interactive API documentation is available via Swagger UI and ReDoc:

-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`
