#!/bin/bash

version=0.1

function log_info() {
  DATE=$(date "+%Y-%m-%d %H:%M:%S")
  echo  "\033[32m$DATE [INFO]: $1 \033[0m"
}

function log_err() {
  DATE=$(date "+%Y-%m-%d %H:%M:%S")
  echo  "\033[31m$DATE [ERROR]: $1 \033[0m"
}

function main(){
    log_info "建置Line推播 Image 中...請稍等" 
    docker build -t howhowline:v0.1 .
    docker images | grep howhowline |awk '{print $2}' | grep $version > /dev/null
    [[ "$?" == "0" ]] || log_err "Image 建置完成失敗，退出程序.." || exit 1
    log_info "Image 已經完成建置"
    log_info "啟動 Container.."
    docker run -it -p 5555:5000 howhowline:v0.1 
}



main