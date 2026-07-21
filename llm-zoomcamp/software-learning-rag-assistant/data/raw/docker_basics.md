# Docker Basics

Docker packages an application and its dependencies into an isolated container. A container runs from an image.

An image is a reusable template that contains the operating system layer, installed packages, application code, and startup command. A container is a running instance of that image.

A Dockerfile describes how to build an image. Common Dockerfile instructions include:

- `FROM` to select the base image
- `WORKDIR` to set the working directory
- `COPY` to copy files into the image
- `RUN` to install dependencies
- `CMD` to define the startup command

Docker Compose is used to run multiple services together. For example, a web application, a database, and a monitoring dashboard can be started with one `docker compose up` command.

For local development, Docker helps make environments reproducible. For production, it helps deploy the same application consistently across machines.

A common mistake is confusing image build time and container runtime. Build-time commands happen when creating the image. Runtime commands happen when the container starts.