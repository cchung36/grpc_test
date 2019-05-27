FROM ubuntu:18.04

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

RUN python3 -m pip install --upgrade -r requirements.txt

RUN mkdir /proto

RUN python3 -m grpc_tools.protoc -I ./proto --python_out=./proto --grpc_python_out=./proto ./proto/data.proto

ENV PYTHONPATH="/app/proto"