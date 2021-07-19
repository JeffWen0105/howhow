FROM python:3.7-alpine3.13
ENV TZ=Asia/Taipei
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
