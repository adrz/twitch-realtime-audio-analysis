FROM frolvlad/alpine-python3:latest

RUN apk upgrade -U \
 && apk add ca-certificates ffmpeg libva-intel-driver gcc musl-dev \
 && rm -rf /var/cache/*

WORKDIR /app
COPY requirements.txt app.py ./
COPY src src

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 5000