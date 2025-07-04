


FROM rabbitmq:3.12-management


WORKDIR /app


ENV RABBITMQ_DEFAULT_USER=admin
ENV RABBITMQ_DEFAULT_PASS=admin123
ENV RABBITMQ_DEFAULT_VHOST=/




EXPOSE 5672 15672


HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD rabbitmq-diagnostics ping || exit 1
