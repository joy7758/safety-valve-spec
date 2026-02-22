FROM python:3.11-slim

WORKDIR /work

# minimal deps
RUN apt-get update -o Acquire::Retries=5 \
 && apt-get install -y --no-install-recommends -o Acquire::Retries=5 curl \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir cryptography fastapi uvicorn

# copy repo into container
COPY . /work

# default shell
CMD ["bash"]
