FROM ubuntu:18.04
RUN mkdir /howhow
ENV LANG=C.UTF-8
ENV TZ=Asia/Taipei
WORKDIR /howhow
RUN apt-get update > /dev/null && apt-get install -y apt-utils > /dev/null && apt-get install python3-dev -y > /dev/null && apt-get install wget -y  > /dev/null && \
  wget https://bootstrap.pypa.io/get-pip.py  > /dev/null && python3 get-pip.py > /dev/null
COPY src/. /howhow
RUN pip3 install -r requestment.txt > /dev/null
EXPOSE 5000
CMD ["python3", "app.py"]

