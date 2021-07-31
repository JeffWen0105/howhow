FROM python:3.7-alpine3.13
RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime \
    && echo "Asia/Taipei" > /etc/timezone \
    && apk del tzdata && apk add sudo
RUN adduser -D howhow
RUN echo 'howhow ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN echo '10 * * * * sh /home/howhow/myCrontab.sh' >> /var/spool/cron/crontabs/root
WORKDIR /home/howhow
COPY requirements.txt .
RUN python -m venv venv
RUN venv/bin/pip install -r  requirements.txt > /dev/null
COPY src/. /home/howhow
RUN chmod +x start*.sh && chmod +x myCrontab.sh
RUN crond > /dev/null
RUN chown -R howhow:howhow /home/howhow
USER howhow
EXPOSE 5000


CMD ["./startup.sh"]
