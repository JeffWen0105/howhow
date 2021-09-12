FROM python:3.7-alpine3.13
RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime \
    && echo "Asia/Taipei" > /etc/timezone \
    && apk del tzdata && apk add --no-cache gcc g++  mysql-dev linux-headers libffi-dev 
RUN adduser -D howhow
WORKDIR /home/howhow
COPY requirements.txt .
RUN python -m venv venv
RUN venv/bin/pip install -r  requirements.txt > /dev/null
COPY SRC/. /home/howhow
RUN chown -R howhow:howhow /home/howhow
RUN chmod +x /home/howhow/startup.sh
USER howhow
EXPOSE 5000


CMD ["./startup.sh"]