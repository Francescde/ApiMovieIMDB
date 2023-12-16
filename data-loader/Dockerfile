FROM python:3.8 as builder

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Download and extract dockerize in a different stage
FROM alpine:latest as downloader

WORKDIR /app

RUN apk --no-cache add curl
RUN curl -L -o dockerize.tar.gz https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize.tar.gz \
    && rm dockerize.tar.gz

# Final image
FROM python:3.8

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY --from=downloader /usr/local/bin/dockerize /usr/local/bin/dockerize

COPY . /app

# Run unit tests
RUN python -m unittest discover tests

ENTRYPOINT ["dockerize", "-wait", "tcp://postgres:5432", "-timeout", "20s", "python", "-u", "load_data.py"]
