FROM python:3.11-slim

WORKDIR /work

# minimal deps
RUN pip install --no-cache-dir cryptography fastapi uvicorn

# copy repo into container
COPY . /work

# default shell
CMD ["bash"]
