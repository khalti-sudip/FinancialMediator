```markdown
## Running the Application with Docker

To run this project using Docker, follow these steps:

### Prerequisites

Ensure you have Docker and Docker Compose installed on your system. Verify the versions meet the requirements specified in the Dockerfiles:
- Docker: 20.10+
- Docker Compose: 1.29+

### Environment Variables

Set up the required environment variables by creating a `.env` file in the project root directory. Refer to the `.env.example` file for the necessary variables and their descriptions.

### Build and Run

1. Build and start the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. The services will be available at the following ports:
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - Frontend: [http://localhost:3000](http://localhost:3000)

### Additional Configuration

- The backend service depends on a PostgreSQL database and Redis for caching and task queuing. These are configured in the `docker-compose.yml` file.
- Modify the `docker-compose.override.yml` file for custom development configurations if needed.

For further details, refer to the respective `Dockerfile` and `docker-compose.yml` files in the project repository.
```