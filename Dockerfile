FROM ubuntu
WORKDIR  /app
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install docker
COPY . .

