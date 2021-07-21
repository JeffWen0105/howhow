###### tags: `Python` `Docker` `Line`

# PTT 上的好康優惠定時發送 至 Line - Docker 容器 

#### 想要收到 PTT 上鄉民提供的優惠嗎 ？ 透過爬蟲可以將數據爬下來，再透過Line 推播就能實現定時自動化唷～～ 快來試試看八

### 基本要求

```
有一個Line 機器人（不需特別啟用 webHook 功能)
ps. 可以至 Line 官網免費建立一個。
```

### Quick Start (Docker 快速部屬)

```bash
docker run -d -p 5000:5000 jeffwen0105/life_money_line_push:0.1 
```

至瀏覽器輸入 `<docker IP>:5000`， 並配置 Line Bot Token 及 Push 的 Line UID， 即可開始使用。  

#### 如何查看 Line Bot Token

![](https://i.imgur.com/OGgksKG.png)


詳情請參考 Line 官網介紹如何快速建置[ Line 機器人 ](https://developers.line.biz/zh-hant/docs/messaging-api/building-bot/#set-up-bot-on-line-developers-console) 。

#### 如何查看 Line 的 UID


* 可以透過 HowHow 的我是誰機器人查詢自己的 UID 或是群組及聊天室的 

![](https://i.imgur.com/lEMeHTH.png)


![](https://i.imgur.com/d9qoRcf.png)


**" 我是誰 " 機器人好友，請掃描QRCODE**


![](https://i.imgur.com/t8AtnMT.png)


---

### GitHub 下載原始碼

[GitHub 請點我](https://github.com/JeffWen0105/howhow/tree/main/Python/Line/lifeIsMoneyLinePush)~~


[整包下載連結點請我](https://downgit.github.io/#/home?url=https://github.com/JeffWen0105/howhow/tree/main/Python/Line/lifeIsMoneyLinePush)~~

### 目錄結構

![](https://i.imgur.com/8KH5CAx.png)


```
1. src => 放置資源主目錄
2. src/app/ => 靜態資源路徑 
3. src/bin => 執行核心程序
4. src/db => DB 儲存
5. app.py => Web Server
6. Dokerfile => 容器映像檔建置
8. requirements.txt => 依賴 Python Lib 列表
```

### 使用方式

```
#  安裝依賴 Lib
1. pip3 install -r requirements.txt 
# 啟動 web 服務（至 src 目錄下執行）
2. gunicorn -w 3 app:app -b 0.0.0.0:5000
# 至瀏覽器輸入 127.0.0.1:5000
3. 配置 Line Bot Token 及 UId 、 GroupID 或是 RoomId
4. 點擊 Run 即可執行程序 或是點擊排程進行定時任務 （排程任務預設每日上午10點半會自動觸發)
```



### DEMO 展示

* 執行 DEMO

![](https://i.imgur.com/LkNFkM0.png)

* Web 介面 DEMO


![](https://i.imgur.com/fMCF0lo.png)


* 設定 Token 及 ID DEMO

![](https://i.imgur.com/r4YJgUl.png)


* 設定排程 DEMO

![](https://i.imgur.com/4HmZQPc.png)
