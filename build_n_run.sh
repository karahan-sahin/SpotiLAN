#!/bin/bash

docker build -t spotilan .
docker run -p 5000:5000 -it spotilan python3 -m src.main