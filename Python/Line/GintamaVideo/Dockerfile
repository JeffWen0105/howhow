FROM python:3.7-alpine3.13
ENV TZ=Asia/Taipei
COPY requirements.txt .
RUN pip3 install  --user  -r requirements.txt > /dev/null
WORKDIR /howhow
COPY src/. /howhow
EXPOSE 5000

CMD ["python3", "app.py"]
