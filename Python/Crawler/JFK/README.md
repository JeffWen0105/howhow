
# Python - 神奇的美女圖片及綱要自動爬取工具

#### 美麗動人的女孩子，人人都愛看，不過能否記錄當下的美好呢？需要自動爬取美女組嗎？並且可以將爬取下來的圖片持久化存放於MongoDB 內， 那一定要來看 HowHow 的教學


### DEMO 使用範例


* 一鍵自動爬取 DEMO

![](https://i.imgur.com/IeJiP04.png)


* MongoDB 爬取內容 DEMO

![](https://i.imgur.com/3aoee1v.png)
![](https://i.imgur.com/tiy72Jf.png)


* Docker 整合，一鍵式完成 工具 + Mongo 部署 DEMO

![](https://i.imgur.com/0XOYtVh.png)


### ~~~~ Source Code 打包[下載請點我](https://downgit.github.io/#/home?url=https://github.com/JeffWen0105/howhow/tree/main/Python/Crawler/JFK) ~~~~


### 更多詳細內容請至 HowHow 的官網查看， [點擊我觀看更多](https://jeffwen0105.com/python_crawler_jkf/)


---

### 使用方式：

```
1. 推薦快速方案 ： Docker 一鍵快速建置方案，如不知道什麼是 Docker那一定要點擊下方的 HowHow Docker 教學 ~
2. 自行部署方案 ： 需自行下載原始碼，並且需要自備 MongoDB 才能使用，且設定檔配置請參考 HowHow 官網說明，將有更多內容。
```


### 項目目錄說明

![](https://i.imgur.com/St6bxnZ.png)

```
1. src： 爬蟲邏輯主程式
2. log : 程式日誌輸入位置
3. requirement.txt : python3 所需要的lib
4. Dockerfile : 建置本地 image
4. docker-compose.yml : Docker 主要執行入口
```

### Docker 使用方式

1. 開啟 docker-compose.yml ，注意紅色框，特別重要，如果要程式能完整啟動一定要輸入 Cookies ，任一 Cookies 會導致有部分資料爬取不到 !!! 至於其他的維持預設值即可，有能力的伙伴也可以自己動手修改 ~

![](https://i.imgur.com/EzPow6y.png)

2. 登入 [JKF 論壇](https://www.jkforum.net/forum.php)（如沒有請先註冊會員) 

```
1. 打開 Chrome 的開發者工具並選擇 網路(network) ，在搜尋框框內填入forum.php後按下重新整理 (需注意篩選條件要為 all)
2. 找到左邊顯示的 forum.php 並點擊
3. 選擇 標頭 (Headers)
4. 往下方找有 cookie 欄位，並將其內容通通複製 （此作法確保爬蟲工具再執行時候是有登入狀態權限)
```



![](https://i.imgur.com/GLSBJYf.jpg)


3. 至 docker-compose.yml ，將複製出來的 cookies 在等號後面直接貼上(不需要加上單引號或是雙引號)

![](https://i.imgur.com/TeaNZ89.png)


4. 確保上述步驟已經完，至終端機執行 docker-compose up -d ，就會自行部署環境了，第一次執行需要拉取本機沒有的 image，需耗時較多時間（依網路下載速度而定）

![](https://i.imgur.com/NxIaFEH.png)

5. Docker 啟動完成後 ， 執行 getData.sh ，將會開始自動爬取資料

```
# 最後的參數為要爬取多少頁面，第一次測試先使用爬一頁
docker-compose exec app sh getData.sh 1
```

![](https://i.imgur.com/Dx9zalm.png)

6. 上述執行指令可以重複執行，會自動驗證該筆資料是否已經存在，如已經存在將不會重複寫入至 MongoDB 內

![](https://i.imgur.com/QAWc9sN.png)


7. 確認已經完成需要爬取的頁面後，可以登入 IP:8081 上查看 howhow DB 並選擇 JKF Collections 是否已經有資料在裡面

![](https://i.imgur.com/Z4AFL7Y.png)



8. 如上述資料都已經正確如庫，可以透過 排程工具 (Linux crontab、Windows工作排程器等) 每天執行該腳本，如該有更新資料將會自動寫入庫內


### 自行部署使用方式:

＊ 詳細內容請至 HowHow 的官網查看， [點擊我觀看更多](https://jeffwen0105.com/python_crawler_jkf/)


[![](https://i.imgur.com/sgdmN00.png)](https://buymeacoffee.com/jeffwen0105)
如果覺得內容還不錯，請我喝杯咖啡吧～


---


<font size="1"><I><b>注： 此工具僅供教學用途，請於下載圖片連結後48小時內刪除，請勿用於商業目的；若有版權問題，使用者必須自行負責。</b></I></font>