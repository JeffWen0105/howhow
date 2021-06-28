#!/bin/bash


function log_info() {
  DATE=$(date "+%Y-%m-%d %H:%M:%S")
  echo -e "\033[32m$DATE [INFO]: $1 \033[0m"
}

pkill promtail

log_info "停止Promtail程序.."
