# Code Editor Project

## Overview

This project is a FastAPI-based application focused on AI-related functionalities. It includes user registration and login, secure authentication using JWT tokens,managing code files and collaboration features like cursor position tracking, highlighting, and text change synchronization. Also it has CRUD operations for  file editing and an enpoint for getting ai solution for given coding snippet.

The project utilizes:

* **FastAPI:** A modern, high-performance web framework for building APIs with Python.
* **Pydantic:** For data validation and serialization.
* **SQLAlchemy:** For database interaction (likely).
* **JWT (JSON Web Tokens):** For authentication.
* **PostgreSQL:** For SQL database interaction.
* **Uvicorn:** An ASGI server for running the FastAPI application.
* **pytest:** For testing.

The project structure includes:

* `api/`: Contains the main application code.
    * `models/`: Defines Pydantic models for request and response data.
    * `schemas/`: PostgreSQL schemas for database tables.
    * `endpoint/`: Contains endpoint definitions for various API functions.
    * `ai_integration/`: For getting the ai suggestions.
    * `core/`: for setting up the data base and other config stuffs.
    * `tests/`: Contains unit tests for the application.
    * `services/`: For commiting the api changes into database.
* `docker-compose.yml`: Defines the Docker services for the application and its dependencies.    

## Getting Started

This guide will help you set up and run Code Editor project on your local machine.

### Prerequisites

* **Docker:** Ensure you have Docker installed on your system. You can find installation instructions for your operating system on the official Docker website.
* **Docker Compose:** Ensure you have Docker Compose installed. It's often included with Docker Desktop, but you might need to install it separately depending on your Docker installation method.


### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/abhirockraj1/CodeEditorGenAi.git
    cd CodeEditorGenAi
    ```
2.  **Ensure Docker and Docker Compose are installed and running on your system.**
3.  **Build and Start Services:** Use Docker Compose to build and start the services defined in `docker-compose.yml`. Run:
    ```bash
    docker-compose build --no-cache
    ```
    ```bash
    docker-compose up
    ```    
    This command will create containers for both the API service and the PostgreSQL database service, link them together, and start them.

3.  **Access the API:** Once the server starts, you can access the API endpoints using a web browser or an HTTP client (like Postman).

    * **Swagger UI (Automatic Documentation):** Navigate to `http://localhost:8000/docs` (or the address and port where your application is running) to view the automatically generated Swagger UI. This provides interactive documentation for your API endpoints.
    * **OpenAPI Specification:** The raw OpenAPI specification (in JSON format) can be found at `http://localhost:8000/openapi.json`.

### API Endpoints
This section describes the API endpoints available for user registration and login, secure authentication using JWT tokens `/users` and are tagged under `users`.

* **`POST /register`:** Registers a new user. Accepts user details (likely email and password) and returns the created user object.
* **`POST /login`:** Logs in an existing user. Accepts username (email) and password, and returns an access token (JWT).
* **`GET /me`:** Retrieves information about the currently authenticated user. Requires a valid access token in the `Authorization` header (Bearer token).

This section describes the API endpoints available for managing code files. These endpoints are prefixed with `/files` and are tagged under `code_files`. From now on Bearer token will be required for all apis

* **`POST /files/`**
    * **Description:** Creates a new code file.
    * **Request Body:** Expects a JSON payload conforming to the `CodeFileCreate` Pydantic model, containing details for the new file (e.g., name, content).
    * **Authentication:** Requires a valid access token to identify the current user, who will be set as the owner of the new file.
    * **Response:**
        * **Status Code:** `201 Created`
        * **Body:** Returns a JSON representation of the newly created `CodeFile` object.

* **`GET /files/{file_id}`**
    * **Description:** Retrieves a specific code file by its unique identifier.
    * **Path Parameter:**
        * `file_id` (integer): The ID of the code file to retrieve.
    * **Authentication:** Requires a valid access token. The requesting user must be either the owner of the file or have been explicitly granted collaborator access.
    * **Response:**
        * **Status Code:** `200 OK`
        * **Body:** Returns a JSON representation of the requested `CodeFile` object.
        * **Status Code:** `404 Not Found` (if the file with the given ID does not exist or the user does not have permission to access it - though permission checks happen before this response in the provided code).

* **`PUT /files/{file_id}`**
    * **Description:** Updates an existing code file.
    * **Path Parameter:**
        * `file_id` (integer): The ID of the code file to update.
    * **Request Body:** Expects a JSON payload conforming to the `CodeFileUpdate` Pydantic model, containing the fields to be updated (e.g., name, content).
    * **Authentication:** Requires a valid access token. Only the owner of the code file is authorized to update it.
    * **Response:**
        * **Status Code:** `200 OK`
        * **Body:** Returns a JSON representation of the updated `CodeFile` object.
        * **Status Code:** `404 Not Found` (if the code file with the given ID does not exist).
        * **Status Code:** `403 Forbidden` (if the requesting user is not the owner of the file).

* **`DELETE /files/{file_id}`**
    * **Description:** Deletes a specific code file by its ID.
    * **Path Parameter:**
        * `file_id` (integer): The ID of the code file to delete.
    * **Authentication:** Requires a valid access token. Only the owner of the code file is authorized to delete it.
    * **Response:**
        * **Status Code:** `204 No Content` (upon successful deletion).
        * **Status Code:** `404 Not Found` (if the code file with the given ID does not exist).
        * **Status Code:** `403 Forbidden` (if the requesting user is not the owner of the file).
        * **Status Code:** `500 Internal Server Error` (if the deletion process fails on the server).

This section describes the API endpoints for real-time collaborative code editing and managing collaborators for code files. These endpoints are prefixed with `/files` and are tagged under `code_files`.

* **`GET /ws/{file_id}` (WebSocket)**
    * **Description:** Establishes a WebSocket connection for real-time collaborative editing of a specific code file.
    * **Path Parameter:**
        * `file_id` (integer): The ID of the code file to collaborate on.
    * **Query Parameter:**
        * `token` (string, required): A valid authentication token (JWT) passed as a query parameter for WebSocket authentication.
    * **Authentication:** Authenticates the user via the provided JWT token in the query parameters. The user must be the owner of the file or an authorized collaborator to establish a connection.
    * **Communication:** Once connected, the WebSocket allows bidirectional communication using JSON messages for:
     * **`text_change`:** Propagates text modifications made by a user to other connected users in real-time. Expects a payload conforming to the `TextChange` Pydantic model.
        * **`cursor_position`:** Broadcasts the current cursor position of a user to other collaborators. Expects a payload conforming to the `CursorPosition` Pydantic model.
        * **`highlight`:** Broadcasts text highlighting actions performed by a user. Expects a payload conforming to the `Highlight` Pydantic model.
        * **`user_joined` (Sent by server):** Notifies connected users when a new user joins the collaborative session.
        * **`initial_content` (Sent by server):** Sends the current content of the code file to a newly connected user.
        * **`user_left` (Sent by server):** Notifies connected users when a user disconnects from the collaborative session.
    * **Disconnection Codes:**
        * `1008 Policy Violation`: Sent by the server if the authentication token is missing, invalid, the user is not authorized to access the file, or if other authentication errors occur.

        * **`expects a payload like this`:**
  ```json
  {
    "type": "text_change",
    "start": 0,
    "delete_count": 17,
    "insert": "Example code modification"
  } 
       
* **`POST /files/{file_id}/add_collaborator`**
    * **Description:** Adds a collaborator to a specific code file.
    * **Path Parameter:**
        * `file_id` (integer): The ID of the code file.
    * **Request Body:** Expects a JSON payload with the key `email` (conforming to a model like `AddCollaborator`) representing the email address of the user to add as a collaborator.
    * **Authentication:** Requires a valid access token. Only the owner of the code file is authorized to add collaborators.
    * **Response:**
        * **Status Code:** `200 OK`
        * **Body:** Returns a JSON representation of the updated `CodeFile` object, including the newly added collaborator (likely in a list of collaborators).
        * **Status Code:** `403 Forbidden` (if the requesting user is not the owner of the file).
        * **Status Code:** `404 Not Found` (if the user with the provided email address does not exist in the system).

* **`POST /files/{file_id}/remove_collaborator`**
    * **Description:** Removes a collaborator from a specific code file.
    * **Path Parameter:**
        * `file_id` (integer): The ID of the code file.
    * **Request Body:** Expects a JSON payload with the key `user_id` (conforming to a model like `RemoveCollaborator`) representing the ID of the user to remove as a collaborator.
    * **Authentication:** Requires a valid access token. Only the owner of the code file is authorized to remove collaborators.
    * **Response:**
        * **Status Code:** `200 OK`
        * **Body:** Returns a JSON representation of the updated `CodeFile` object, with the specified user removed from the list of collaborators.
        * **Status Code:** `403 Forbidden` (if the requesting user is not the owner of the file).
        * **Status Code:** `404 Not Found` (if the user with the provided ID is not found or is not a collaborator on this file).

This section describes the API endpoint for analyzing code using an AI debugging service. This endpoint is prefixed with `/ai_debugging` and tagged under `ai_debugging`. This api don't require any authentication.

* **`POST /ai_debugging/analyze_code`**
    * **Description:** Analyzes the provided code snippet using an AI model (specifically OpenRouter AI, based on the docstring). This endpoint can help identify potential bugs, suggest improvements, or provide insights based on the code and specified programming language.
    * **Request Body:** Expects a JSON payload conforming to the `CodeAnalysisRequest` Pydantic model, which should include:
        * `code` (string, required): The code snippet to be analyzed.
        * `language` (string, required): The programming language of the provided code (e.g., "python", "javascript", "java").
    * **Authentication:** While not explicitly shown in the code snippet, this endpoint might or might not require authentication depending on the overall application's security policy. Refer to the broader security documentation.
    * **Rate Limiting:** This endpoint is rate-limited to a maximum of 5 requests per minute from the same client IP address. Exceeding this limit will likely result in a `429 Too Many Requests` error.
    * **Response:**
        * **Status Code:** `200 OK`
        * **Body:** Returns a JSON object conforming to the `CodeAnalysisResponse` Pydantic model, containing:
            * `suggestions` (list of strings): A list of suggestions or insights generated by the AI model based on the provided code.
        * **Status Code:** `400 Bad Request` (if the request body is invalid or missing required fields).
        * **Status Code:** `429 Too Many Requests` (if the client has exceeded the rate limit).
        * **Status Code:** `500 Internal Server Error` (if there is an error communicating with the AI service or during the analysis process).

# Data Model Definition

This document outlines the data model used in the application, defined using SQLAlchemy for database interaction and Pydantic for data validation.

## SQLAlchemy Models

These classes define the structure of the database tables.

### `User`

Represents a user in the system.

| Column          | Data Type | Constraints                     | Description                               |
|-----------------|-----------|---------------------------------|-------------------------------------------|
| `id`            | Integer   | Primary Key, Index              | Unique identifier for the user.           |
| `email`         | String    | Unique, Index                   | User's email address (must be unique).    |
| `hashed_password`| String    |                                 | Securely stored hashed password.          |
| `is_active`     | Boolean   | Default: `True`                 | Indicates if the user account is active. |
| `owned_files`   | Relationship | `CodeFile`, `back_populates="owner"` | Collection of code files owned by the user. |
| `collaborations`| Relationship | `CodeFile`, `secondary="collaborations_table"`, `back_populates="collaborators"` | Collection of code files the user is collaborating on. |
| `editing_sessions`| Relationship | `EditingSession`, `back_populates="user"` | Collection of editing sessions for the user. |

### `Collaboration` (`collaborations_table`)

Represents the association between users and the code files they collaborate on. This is a secondary table for the many-to-many relationship between `User` and `CodeFile`.

| Column   | Data Type | Foreign Key          | Primary Key (Part of) | Description                                  |
|----------|-----------|----------------------|-----------------------|----------------------------------------------|
| `user_id`| Integer   | `users.id`           | Yes                   | Foreign key referencing the `User` table.    |
| `file_id`| Integer   | `code_files.id`      | Yes                   | Foreign key referencing the `CodeFile` table. |

### `CodeFile`

Represents a code file stored in the system.

| Column       | Data Type | Constraints                     | Foreign Key          | Description                                     |
|--------------|-----------|---------------------------------|----------------------|-------------------------------------------------|
| `id`         | Integer   | Primary Key, Index              |                      | Unique identifier for the code file.            |
| `filename`   | String    | Index                           |                      | Name of the code file.                          |
| `content`    | String    |                                 |                      | The actual content of the code file.            |
| `owner_id`   | Integer   |                                 | `users.id`           | Foreign key referencing the `User` who owns the file. |
| `created_at` | DateTime  | Default: `func.now()`           |                      | Timestamp when the file was created.            |
| `updated_at` | DateTime  | Default: `func.now()`, `onupdate=func.now()` |                      | Timestamp when the file was last updated.       |
| `owner`      | Relationship | `User`, `back_populates="owned_files"` |                      | The user who owns this code file.               |
| `collaborators`| Relationship | `User`, `secondary="collaborations_table"`, `back_populates="collaborations"` |                      | Collection of users collaborating on this file. |
| `editing_sessions`| Relationship | `EditingSession`, `back_populates="code_file"` |                      | Collection of editing sessions for this file. |

### `EditingSession`

Represents a period when a user is actively editing a code file.

| Column        | Data Type | Constraints                     | Foreign Key          | Description                                     |
|---------------|-----------|---------------------------------|----------------------|-------------------------------------------------|
| `id`          | Integer   | Primary Key, Index              |                      | Unique identifier for the editing session.        |
| `user_id`     | Integer   |                                 | `users.id`           | Foreign key referencing the `User` in the session. |
| `file_id`     | Integer   |                                 | `code_files.id`      | Foreign key referencing the `CodeFile` being edited. |
| `session_start`| DateTime  | Default: `func.now()`           |                      | Timestamp when the editing session started.       |
| `session_end` | DateTime  | Nullable: `True`                |                      | Timestamp when the editing session ended (can be null if active). |
| `user`        | Relationship | `User`, `back_populates="editing_sessions"` |                      | The user involved in this editing session.      |
| `code_file`   | Relationship | `CodeFile`, `back_populates="editing_sessions"` |                      | The code file being edited in this session.    |

## Pydantic Models

These classes define the expected structure for data input and output, used for validation and serialization.

### `AddCollaborator`

Defines the expected data structure for adding a collaborator to a code file.

| Field   | Data Type | Description                         |
|---------|-----------|-------------------------------------|
| `email` | `str`     | The email address of the user to add. |

### `RemoveCollaborator`

Defines the expected data structure for removing a collaborator from a code file.

| Field     | Data Type | Description                                |
|-----------|-----------|--------------------------------------------|
| `user_id` | `int`     | The ID of the user to remove as a collaborator. |

---

This information provides a clear overview of the data structure used in the application.

### Contact

[abhinav Kumar]
[abhinavkool19@gmail.com]