#!/bin/bash

function log_info() {
  DATE=$(date "+%Y-%m-%d %H:%M:%S")
  echo -e "\033[32m$DATE [INFO]: $1 \033[0m"
}

function log_err() {
  DATE=$(date "+%Y-%m-%d %H:%M:%S")
  echo -e "\033[31m$DATE [ERROR]: $1 \033[0m"
}

pkill promtail
nohup ./bin/promtail-linux-amd64 -config.file=conf/config-promtail.yml  > running.log 2>&1 &

 [[ "$?" == "0" ]] && log_info "\n1.成功於背景執行Promtail\n2.停止請執行sh stop_promtail.sh\n3.執行 Log 進度，請使用tail -f running.log" || log_err "執行異常，請查看 running.log"
 
