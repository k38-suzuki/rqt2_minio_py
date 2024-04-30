FROM ubuntu:latest

RUN apt update && apt install -y python3-boto3 wget

WORKDIR /var

RUN wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20230322063624.0.0_amd64.deb -O minio.deb

RUN dpkg -i minio.deb

CMD [ "minio", "server", "~/minio", "--console-address", ":9090" ]
