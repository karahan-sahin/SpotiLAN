FROM python:3.8-slim-buster

WORKDIR /app

# Install net-tools to get ifconfig
RUN apt-get update && \
    apt-get install -y net-tools && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000

COPY . .
