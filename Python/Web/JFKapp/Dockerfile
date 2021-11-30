FROM python:3.7-alpine3.13
RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime \
    && echo "Asia/Taipei" > /etc/timezone \
    && apk del tzdata
RUN adduser -D howhow
RUN echo 'howhow ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
WORKDIR /home/howhow
COPY requirements.txt .
RUN python -m venv venv
RUN venv/bin/python -m pip install --upgrade pip > /dev/null
RUN venv/bin/pip install -r  requirements.txt > /dev/null
COPY src/. /home/howhow
RUN chmod +x *.sh
RUN chown -R howhow:howhow /home/howhow
USER howhow
EXPOSE 5000


CMD ["./startup.sh"]