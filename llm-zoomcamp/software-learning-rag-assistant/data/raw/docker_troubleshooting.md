# Docker Troubleshooting

When Docker does not work, start by checking whether Docker Desktop is running. On Windows, Docker Desktop usually depends on WSL 2.

If the terminal says `docker is not recognized`, the Docker CLI is not installed or not available in PATH. Restarting the terminal after installation often fixes this.

If Docker Desktop says WSL is not installed, install Windows Subsystem for Linux and restart the computer. Docker Desktop uses WSL 2 as the backend on modern Windows setups.

If a container is running but `localhost` does not respond, check the port mapping. A container port must be published to the host, for example `8080:8080`.

If `docker compose up` fails, check the `docker-compose.yml` indentation, image name, environment variables, and mounted volumes.

If a container exits immediately, inspect logs with `docker logs <container>` or `docker compose logs`.

A good debugging flow is:

1. Check Docker Desktop status
2. Check `docker --version`
3. Check `docker compose version`
4. Check running containers with `docker ps`
5. Inspect logs
6. Verify ports and environment variables