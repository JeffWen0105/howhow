#!/bin/bash

function log_info() {
  DATE=$(date "+%Y-%m-%d %H:%M:%S")
  echo -e "\033[32m$DATE [INFO]: $1 \033[0m"
}

function log_err() {
  DATE=$(date "+%Y-%m-%d %H:%M:%S")
  echo -e "\033[31m$DATE [ERROR]: $1 \033[0m"
}

function check_release(){
  os=$(hostnamectl | grep 'Operating System' | grep "Red\|CentOS")
  if [[ $os == '' ]]; then
    log_err "目前僅支援CentOS 或Red Hat 系列安裝..."
    exit 1
  else
    os=$(hostnamectl | grep 'Operating System' | grep "CentOS")
      [[ $os != '' ]] && log_info "檢測版本為CentOS 系列.." || log_info "檢測版本為Red Hat 系列.."
  fi
}

function docker_check(){
  sudo docker --help > /dev/null
  [[ "$?" == "1" ]] && sudo systemctl start docker
  [[ "$?" == "127" ]] && docker_installer
  sudo docker-compose --help > /dev/null
  [[ "$?" == "1" ]] && docker_compose_installer
}


function docker_installer() {
  log_info "開始安裝Docker程序..請稍等"
  sudo yum install -y yum-utils
  sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
  sudo yum install docker-ce docker-ce-cli containerd.io -y
  log_info "Dokcer安裝完畢，並啟動服務及開機自動載入..."
  sudo systemctl start docker
  sudo systemctl enable docker
  log_info "執行Hello World image"
  sudo docker run hello-world
}

function docker_compose_installer(){
  log_info "安裝Docker Compose..請稍等"
  sudo curl -L "https://github.com/docker/compose/releases/download/1.28.6/docker-compose-$(uname -s)-$(uname -m)" \
   -o /bin/docker-compose && \
  sudo chmod +x /bin/docker-compose
  docker-compose --version
}

function loki_installer(){
  log_info "部署Loki及Grafana..請稍等"
  mkdir -p ~/howhow/loki &&  \
  sudo mkdir -p /mnt/rawdata/howhow/loki/conf  && \
  cd ~/howhow/loki && \
  sudo mkdir -p /mnt/rawdata/howhow/loki/data && sudo mkdir -p /mnt/rawdata/howhow/loki/config
  sudo wget -q https://jeffwen0105.github.io/howhow/Linux/Loki/conf/local-config.yaml \
   -O /mnt/rawdata/howhow/loki/config/local-config.yaml
  sudo chmod -R 777 /mnt/rawdata/howhow/loki/ && \
  sudo chmod -R 777 /mnt/rawdata/howhow/loki/data
  wget -q https://jeffwen0105.github.io/howhow/Linux/Loki/Docker/docker-compose.yml \
   -O docker-compose.yml
  sudo docker-compose up -d
  loki_init
}

function loki_init(){
  log_info "初始化promtail..."
  lib_check
  cd ~/howhow/loki
  mkdir -p  promtail/bin && mkdir -p promtail/log && mkdir -p promtail/conf
  [[ "$?" == "0" ]] && log_info "創建 bin log conf 目錄.." || \
  log_err "創建 bin log conf 目錄失敗，請檢查權限...\n程式結束" || exit 1
  log_info "下載promtail主程式..請稍等"
  cd promtail/bin && wget -q  https://github.com/grafana/loki/releases/download/v2.2.1/promtail-linux-amd64.zip\
   -O promtail-linux-amd64.zip && unzip "promtail-linux-amd64.zip"  > /dev/null
  chmod 755 promtail-linux-amd64
  log_info "下載promtail組態檔及執行腳本..請稍等"
  cd ../conf && wget -q https://jeffwen0105.github.io/howhow/Linux/Loki/conf/config-promtail.yml  -O config-promtail.yml
  sed -i 's+log/promtail.yml+/home/sa_cluster/howhow/loki/promtail/log/promtail.yml+g' config-promtail.yml
  sed -i 's+192.168.50.195+127.0.0.1+g' config-promtail.yml
  ls /sensorsdata/main/logs/sbp/web/*.log > /dev/null
  [[ "$?" == "0" ]] && \
   sed -i 's+/var/log/\*.log+/sensorsdata/main/logs/sbp/web/\*.log.\*+g' config-promtail.yml || \
   sed -i 's+/var/log/\*.log+/data/sa_cluster/logs/sa/web/\*.log.\*+g' config-promtail.yml
  cd .. &&  wget -q https://jeffwen0105.github.io/howhow/Linux/Loki/script/start_promtail.sh -O start_promtail.sh \
   && chmod 755 start_promtail.sh && wget -q https://jeffwen0105.github.io/howhow/Linux/Loki/script/stop_promtail.sh \
    -O stop_promtail.sh && chmod 755 stop_promtail.sh
  sed -i 's+./bin/promtail-linux-amd64+/home/sa_cluster/howhow/loki/promtail/bin/promtail-linux-amd64+g' start_promtail.sh  
  sed -i 's+=conf/config-promtail.yml+=/home/sa_cluster/howhow/loki/promtail/conf/config-promtail.yml+g' start_promtail.sh
  sudo ln -s /home/sa_cluster/howhow/loki/promtail/start_promtail.sh /usr/bin/start_promtail.sh
  sudo ln -s /home/sa_cluster/howhow/loki/promtail/stop_promtail.sh /usr/bin/stop_promtail.sh
  log_info "$(pwd)目錄狀態為："
  ls -lh
  log_info "\n程序執行完畢，請使用 sh start_promtail.sh 執行程序，會自動抓取 SBP 所有 web Log"
  log_info "請至Grafana -> http://$(hostname -i):3000  上配置Loki數據來源"
  log_info "如何配置，請掃描QRcode參考HowHow的說明："
  qrencode -m 2 -t utf8 <<<  "qrencode -m 2 -t utf8 <<<  "https://jeffwen0105.com/grafana""
}

function lib_check(){
  unzip -h > /dev/null
  [[ "$?" != "0" ]] && yum install -y zip > /dev/null
  qrencode -V > /dev/null
  [[ "$?" != "0" ]] && yum install -y qrencode > /dev/null
}

if [[ $(whoami) != "sa_cluster" ]]; then
  log_err "請使用 sa_cluster "
  exit 1
fi

check_release
docker_check
loki_installer