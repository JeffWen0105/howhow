###### tags: `Python`

# Python - 美女圖推播系統 (整合自動爬取 ＋ Line 推播 ＋ 應用界面)


#### 透過爬取的綱要及Line 推播可以順利的推送，不過其實並不是方便，也無法看到預覽圖，接下來跟隨者 HowHow 手把手代你打造屬於自己整推播系統 ~~


### DEMO 使用範例

1. 應用界面 DEMO

![](https://i.imgur.com/k1EDTdl.jpg)


2. 限定帳密登入 DEMO


3. 最末頁提示沒有圖片 DEMO

![](https://i.imgur.com/fqtFLOC.png)



4. 發送推播 DEMO

![](https://i.imgur.com/xQt2vPg.png)

5. Line 群組接收 DEMO

![](https://i.imgur.com/bWAtdmx.png)



* Docker 整合，一鍵式完成 工具 + Mongo 部署 DEMO

![](https://i.imgur.com/0XOYtVh.png)




---

### 使用方式：

```
1. 推薦快速方案 ： Docker 一鍵快速建置方案，如不知道什麼是 Docker那一定要點擊下方的 HowHow Docker 教學 ~
2. 自行部署方案 ： 需自行下載原始碼，並且需要自備 MongoDB 才能使用，且設定檔配置請參考 HowHow 官網說明，將有更多內容。
```


### 項目目錄說明

* 主目錄

![](https://i.imgur.com/St6bxnZ.png)

```
1. src： 應用主程式
2. log : 程式日誌輸入位置
3. requirement.txt : python3 所需要的lib
4. Dockerfile : 建置本地 image
4. docker-compose.yml : Docker 主要執行入口
```

*  src 核心目錄

```
1. app 資料夾 : HTML、CSS、JS 等靜態資源
2. db 資料夾 ： SQLite 存放
3. log 資料夾 : 程式日誌輸入位置
4. crawlerData.py : 自動爬取綱要程序
5. getData.sh :  封裝的自動爬取綱要程序，容器化使用
6. postData.py ： 透過取得 HashID 爬取圖片並推送至 Line
7. db.py : SQLite 封裝控制程序
8. myPyMongo.py : Mongo 封裝控制程序
9. app.py ： Web 應用程式
10. startup.sh ： 容器主程序啟動的入口
```



### Docker 使用方式

1. 編輯 docker-compose.yml ，注意紅色框，特別重要，如果要程式能完整啟動一定要輸入 Cookies ，任一 Cookies 會導致有部分資料爬取不到 !!! 至於其他的維持預設值即可，有能力的伙伴也可以自己動手修改 ~


![](https://i.imgur.com/5dp4mi3.png)

* 一定要修改的部分爲 : 

```
1. LineToken -> Line Notify 產生的群組 Token
2. JKFcookie -> JKF 登入過後的使用者 Cookies
```

LineToken 取的方式請依造 HowHow 官網的 : Python – Line Notify (含註冊教學) + Python API 串接 教學執行，[連結傳送門請點我](https://jeffwen0105.com/python_linenotify/)

JKFcookie 取的方式請依造 HowHow 官網的 : Python – 神奇的美女圖片及綱要自動爬取工具 中的 使用方式，[連結傳送門請點我](https://jeffwen0105.com/python_crawler_jkf/)

* 可以自行修改部分 :

```
3. userName -> 介面登入的帳號，預設爲 howhow，可以自行修改
4. userPasswd -> 介面登入的密碼,預設爲 800101，可以自行修改
5. myMongoIP -> MongoDB的IP，預設使用容器 howhowmongo 域名，可以自行修改自己的 MongoDB IP （port 必須爲 27017）
```

2. 確保上述步驟已經完，至終端機執行 docker-compose up -d ，就會自行部署環境了，第一次執行需要拉取本機沒有的 image，需耗時較多時間（依網路下載速度而定）

![](https://i.imgur.com/NxIaFEH.png)

3. Docker 啟動完成後 ， 執行 getData.sh ，將會開始自動爬取資料

```
# 最後的參數為要爬取多少頁面，第一次測試先使用爬一頁
docker-compose exec web sh getData.sh 1
```

![](https://i.imgur.com/Dx9zalm.png)

6. 上述執行指令可以重複執行，會自動驗證該筆資料是否已經存在，如已經存在將不會重複寫入至 MongoDB 內

![](https://i.imgur.com/QAWc9sN.png)


7. 確認已經完成需要爬取的頁面後，可以登入 IP:8081 上查看 howhow DB 並選擇 JKF Collections 是否已經有資料在裡面

![](https://i.imgur.com/Z4AFL7Y.png)



8. 如上述資料都已經正確如庫，可以登入  IP:5858 上輸入帳號密碼並登入應用程式並嘗試進行推播

![](https://i.imgur.com/xQt2vPg.png)

9.　至 Line 群組查看訊息

![](https://i.imgur.com/bWAtdmx.png)

---




### 自行部署方式：

* 請至 HowHow 的官網查看， 點擊我觀看更多

* 執行前準備事項

```
1. 具備 python3.6 以上直譯器
2. 具備 Mongodb ， 並確保有權可以訪問並且創建 index，必須確保 27017 阜號暢通
3. 具備 JKF 會員
```

1. 下載原始碼，整包[下載請點我](https://downgit.github.io/#/)

2. 解開原始碼包後，透過 pip 安裝 Python所需套件

```
pip3 install -r requirements.txt
```

3. 輸入必要的環境變數

```
1. LineToken -> Line Notify 產生的群組 Token

export LineToken="xxxx"

2. JKFcookie -> JKF 登入過後的使用者 Cookies

export JKFcookie="zzzz"

3. myMongoIP -> MongoDB的IP ， 預設爲 127.0.0.1 ，可以自行修改自己的 MongoDB IP （port 必須爲 27017）

export myMongoIP='yy.yy.yy.yy'

4. userName -> 介面登入的帳號，預設爲 howhow，可以自行修改

export userName='www'

5. userPasswd -> 介面登入的密碼,預設爲 800101，可以自行修改

export userPasswd='ddd'
```

LineToken 取的方式請依造 HowHow 官網的 : Python – Line Notify (含註冊教學) + Python API 串接 教學執行，[連結傳送門請點我](https://jeffwen0105.com/python_linenotify/)

JKFcookie 取的方式請依造 HowHow 官網的 : Python – 神奇的美女圖片及綱要自動爬取工具 中的 使用方式，[連結傳送門請點我](https://jeffwen0105.com/python_crawler_jkf/)

4. 啟動 app 應用程式 ，　預設 port 爲 5000

```
sh startup.sh
```

5. 執行爬取綱要 crawlerData.py 腳本 ，將會開始自動爬取資料

```
# 最後的參數為要爬取多少頁面，第一次測試先使用爬一頁
python3 crawlerData.py 1
```

6. 上述執行指令可以重複執行，會自動驗證該筆資料是否已經存在，如已經存在將不會重複寫入至 MongoDB 內

![](https://i.imgur.com/QAWc9sN.png)





7. 如上述資料都已經正確如庫，可以登入  IP:5000 上輸入帳號密碼並登入應用程式並嘗試進行推播

![](https://i.imgur.com/xQt2vPg.png)



8. 如上述資料都已經正確如庫，可以透過 排程工具 (Linux crontab、Windows工作排程器等) 每天執行該腳本，如該有更新資料將會自動寫入庫內



[![](https://i.imgur.com/sgdmN00.png)](https://buymeacoffee.com/jeffwen0105)
如果覺得內容還不錯，請我喝杯咖啡吧～


<font size="0.1"><I><b>注： 此工具僅供教學用途，請於下載圖片連結後48小時內刪除，請勿用於商業目的；若有版權問題，使用者必須自行負責。</b></I></font>