#FROM ubuntu:latest
#LABEL authors="Tarik Salay"
#
#ENTRYPOINT ["top", "-b"]

# Dockerfile to create the image
# There are images ready to use in DockerHub for common services such as PostgreSQL etc.

# Image
FROM rabbitmq:3.12-management

# Directory
WORKDIR /app

# Set environment variables
ENV RABBITMQ_DEFAULT_USER=admin
ENV RABBITMQ_DEFAULT_PASS=admin123
ENV RABBITMQ_DEFAULT_VHOST=/

# Copy custom configuration if needed
# COPY rabbitmq.conf /etc/rabbitmq/

# Expose ports
EXPOSE 5672 15672

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD rabbitmq-diagnostics ping || exit 1
