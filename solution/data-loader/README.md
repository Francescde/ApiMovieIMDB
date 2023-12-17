The error "exec format error" typically indicates a compatibility issue between the binary and the operating system or architecture. In this case, it seems that the `dockerize` binary you downloaded may not be compatible with your system.

Here's an alternative approach that should work across different systems. Instead of using `curl` to download and install `dockerize`, you can use the multi-stage build approach:

```Dockerfile
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

COPY . /app

# Run unit tests
RUN python -m unittest discover tests

ENTRYPOINT ["dockerize", "python", "-u", "load_data.py"]
```

This Dockerfile uses a multi-stage build. In the first stage (`builder`), it installs the Python dependencies. In the second stage (`downloader`), it downloads and extracts `dockerize` using Alpine Linux, which is a lightweight base image. The final image then copies the necessary files from the builder stage and continues with the rest of the setup.

This approach should help avoid compatibility issues.

----------------------------------------------------------------------------------------------------

It appears that the error is related to the `dockerize` command not being found in the container's `$PATH`. This could be due to the fact that the `dockerize` binary is not present in the final image or is not located in a directory included in the `$PATH`.

Let's modify the Dockerfile to ensure that `dockerize` is correctly included in the final image:

```Dockerfile
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

ENTRYPOINT ["dockerize", "python", "-u", "load_data.py"]
```

This modification adds the line `COPY --from=downloader /usr/local/bin/dockerize /usr/local/bin/dockerize` to copy the `dockerize` binary from the `downloader` stage to the final image. This should resolve the "executable file not found" issue.

After making these changes, rebuild your Docker image and try running it again.