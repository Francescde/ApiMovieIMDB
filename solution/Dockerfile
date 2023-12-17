# Builder stage
FROM python:3.8 as builder

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Downloader stage
FROM alpine:latest as downloader

WORKDIR /app

RUN apk --no-cache add curl
RUN curl -L -o dockerize.tar.gz https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize.tar.gz \
    && rm dockerize.tar.gz

# Final image
FROM python:3.8

WORKDIR /app

# Copy dependencies from the builder stage
COPY --from=builder /usr/local /usr/local

# Copy dockerize from the downloader stage
COPY --from=downloader /usr/local/bin/dockerize /usr/local/bin/dockerize

# Copy the rest of the application
COPY . /app

# Set the working directory for the API tests
WORKDIR /app/api
# Run unit tests
RUN python -m unittest discover tests

# Set the working directory for the data-loader tests
WORKDIR /app/data-loader
# Run unit tests
RUN python -m unittest discover tests

# Reset the working directory to the root
WORKDIR /app

# Entrypoint for the application
ENTRYPOINT ["dockerize", "-wait", "tcp://postgres:5432", "-timeout", "20s", "./run.sh"]
