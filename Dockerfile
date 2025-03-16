FROM python:3.10-alpine

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV TZ=Asia/Shanghai
RUN apk update && apk add --no-cache tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

CMD [ "python", "main.py" ]