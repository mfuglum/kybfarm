# kybfarm
Open-source IoT platform for Vertical Farming Facilities.

## Docker Compose: Build and launch the containers
Prerequisite: Docker Desktop is installed.

For local development the tunnel container 'cloudlfared' can be commented out.

In root folder of the cloned repo the following command builds and launches the containers:
``` bash
docker compose -f kybfarm-docker-compose.yaml up --build -d
```
