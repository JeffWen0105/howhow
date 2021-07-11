#!/bin/bash

function log_info() {
  DATE=$(date "+%Y-%m-%d %H:%M:%S")
  echo -e "\033[32m$DATE [INFO]: $1 \033[0m"
}

function log_err() {
  DATE=$(date "+%Y-%m-%d %H:%M:%S")
  echo -e "\033[31m$DATE [ERROR]: $1 \033[0m"
}


function main(){
    log_info "建置Line推播映像檔中...請稍等"
    docker build -t howhowline:v0.1 .
    
}