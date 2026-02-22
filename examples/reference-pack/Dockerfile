FROM python:3.11-slim

WORKDIR /work

# minimal deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir cryptography fastapi uvicorn

# copy repo into container
COPY . /work

# default shell
CMD ["bash"]
