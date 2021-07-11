FROM python:3.7-alpine3.13
ENV TZ=Asia/Taipei
COPY requestment.txt .
RUN pip3 install  --user  -r requestment.txt > /dev/null
WORKDIR /howhow
COPY src/. /howhow
EXPOSE 5000

CMD ["python3", "app.py"]