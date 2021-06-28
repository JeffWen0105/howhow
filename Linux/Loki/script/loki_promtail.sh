#!/bin/bash


function log_info() {
  DATE=$(date "+%Y-%m-%d %H:%M:%S")
  echo -e "\033[32m$DATE [INFO]: $1 \033[0m"
}

function log_err() {
  DATE=$(date "+%Y-%m-%d %H:%M:%S")
  echo -e "\033[31m$DATE [ERROR]: $1 \033[0m"
}

function check_lib(){
  wget -h > /dev/null
  [[ "$?" != "0" ]] && log_err "缺少 wget 套件，請先下載..程式結束" && exit 1
  unzip -h > /dev/null
  [[ "$?" != "0" ]] && log_err "缺少 zip 套件，請先下載..程式結束" && exit 1
}

function main(){
  mkdir -p  promtail/bin && mkdir -p promtail/log && mkdir -p promtail/conf
  [[ "$?" == "0" ]] && log_info "創建 bin log conf 目錄.." || log_err "創建 bin log conf 目錄失敗，請檢查權限...\n程式結束" || exit 1
  log_info "下載promtail主程式...請稍等"
  cd promtail/bin && wget -q  https://github.com/grafana/loki/releases/download/v2.2.1/promtail-linux-amd64.zip -O promtail-linux-amd64.zip && unzip "promtail-linux-amd64.zip"  > /dev/null
  chmod 755 promtail-linux-amd64
  log_info "下載promtail組態檔及執行腳本..請稍等"
  cd ../conf && wget -q https://jeffwen0105.github.io/howhow/Linux/Loki/conf/config-promtail.yml  -O config-promtail.yml
  cd .. &&  wget -q https://jeffwen0105.github.io/howhow/Linux/Loki/script/start_promtail.sh -O start_promtail.sh \
   && chmod 755 start_promtail.sh && wget -q https://jeffwen0105.github.io/howhow/Linux/Loki/script/stop_promtail.sh -O stop_promtail.sh && chmod 755 stop_promtail.sh
  log_info "$(pwd)目錄狀態為："
  ls -lh
  log_info "\n程序執行完畢，請至 promtail/conf 內修改配置檔，並透過 start_promtail.sh 執行程序"
}

check_lib
log_info "歡迎使用 Loki 洛基 Agent 自動下載程式..."
main
[[ "$?" != "0" ]] && log_err "程序異常，請排查完再執行.."