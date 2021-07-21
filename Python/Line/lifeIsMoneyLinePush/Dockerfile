FROM python:3.7-alpine3.13
RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime \
    && echo "Asia/Taipei" > /etc/timezone \
    && apk del tzdata
RUN adduser -D howhow
WORKDIR /home/howhow
COPY requirements.txt .
RUN python -m venv venv
RUN venv/bin/pip install -r  requirements.txt > /dev/null
COPY src/. /home/howhow
RUN chmod +x start*.sh
RUN chown -R howhow:howhow /home/howhow
USER howhow
EXPOSE 5000


CMD ["./startup.sh"]
