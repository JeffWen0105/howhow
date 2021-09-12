


# 使用Flask 製作簡單的登入（出）網頁 - REDEME


### [打包下載請點我](https://downgit.github.io/#/home?url=https://github.com/JeffWen0105/howhow/tree/main/Python/Web/Flask_login)

#### 使用說明:

```
1. 方案一 ： 預設方式啟動 Web，需自備 MySQL 及訪問權限
2. 方案二 ： 預設方式啟動 Web ，及使用 HowHow 建置的 Database Docker 容器
3. 方案三 ： 全部都使用 HowHow DB 及 Web 容器 
```



| 方案一 | 方案二 | 方案三 |
| -------- | -------- | -------- |
| 全自主配置     | 半自動配置     | 全自動配置     |
|需自備DB    |無須自備DB    |無須自備DB    |
|Web lib自行安裝|Web lib自行安裝|無須安裝lib|
|無須Docker|須Docker|須Docker|


### 方案一：

#### 1. 下載相關Python套件:

pip install -r requirements.txt

* 如沒有 GCC 或是 mysql-client 的 lib 需先安裝

#### 2. 創建SQL表

```
/* MySQL */
create table users ( id int not null auto_increment, name varchar(20) not null, email varchar(20) not null, password char(80) not null, primary key (id) );
```


#### 3. 修改程式碼內MySQL的登入帳號、密碼、資料庫名稱、資料庫IP:

```
# ex. Python:
app.config['MYSQL_HOST'] = '127.0.0.1'          # 登入ip
app.config['MYSQL_USER'] = 'root'               # 登入帳號
app.config['MYSQL_PASSWORD'] = 'root'           # 登入密碼
app.config['MYSQL_DB'] = 'db'                   # 登入資料庫名稱
```

#### 4. 執行程式方式

```
python3 app.py
```

#### 5. 至瀏覽器輸入 IP:5000


注: 
	1. 請確保MySQL可以正常運作
	2. 更詳細操作步驟[請參閱HowHowWen官網](https://jeffwen0105.com/python-%E4%BD%BF%E7%94%A8flask-%E8%A3%BD%E4%BD%9C%E7%B0%A1%E5%96%AE%E7%9A%84%E7%99%BB%E5%85%A5%E5%8F%8A%E7%99%BB%E5%87%BA%E7%B6%B2%E7%AB%99/)


---

### Docker 快速部署 DEMO


1. 一鍵式快速部署

![](https://i.imgur.com/SCQI8dR.png)


2. DB管理介面

![](https://i.imgur.com/g33nswd.png)

3. Docker-compose 彈性 Yaml 自行配置



![](https://i.imgur.com/JzcpayJ.png)

4. Dockerfile 免去安裝套件環境問題

![](https://i.imgur.com/fcIxnVC.png)



---

### 方案二(使用HowHow 的 DB)：

* 需具備 Docker 及 Docker-compose ， [安裝方式請參閱HowHow官網](https://jeffwen0105.com/dokcer-%e8%b2%a8%e6%ab%83%e5%ae%b9%e5%99%a8%e5%85%a9%e4%b8%89%e4%ba%8b/)




#### 1. 下載相關Python套件:

```
pip install -r requirements.txt
```


* 如沒有 GCC 或是 mysql-client 的 lib 需先安裝


#### 2. 切換至 DB_on_Dokcer 資料夾啟動容器：

```
docker-compose up
```

#### 3. 修改程式碼內MySQL的登入帳號、密碼、資料庫名稱、資料庫IP:

```
# ex. Python:
app.config['MYSQL_HOST'] = '<Docker DB IP>'     # 登入ip
app.config['MYSQL_USER'] = 'root'               # 登入帳號
app.config['MYSQL_PASSWORD'] = 'root'           # 登入密碼
app.config['MYSQL_DB'] = 'db'                   # 登入資料庫名稱
```

#### 4. 執行程式方式

```
python3 app.py
```

#### 5. 至瀏覽器輸入 IP:5000

 
	
* 更詳細操作步驟[請參閱HowHowWen官網](https://jeffwen0105.com/python-%E4%BD%BF%E7%94%A8flask-%E8%A3%BD%E4%BD%9C%E7%B0%A1%E5%96%AE%E7%9A%84%E7%99%BB%E5%85%A5%E5%8F%8A%E7%99%BB%E5%87%BA%E7%B6%B2%E7%AB%99/)

---

### 方案三(使用HowHow 的 DB + Web 容器)：


* 需具備 Docker 及 Docker-compose ， [安裝方式請參閱HowHow官網](https://jeffwen0105.com/dokcer-%e8%b2%a8%e6%ab%83%e5%ae%b9%e5%99%a8%e5%85%a9%e4%b8%89%e4%ba%8b/)

#### 1. 切換至 Demo_on_Dokcer 資料夾啟動容器：

```
docker-compose up
```

#### 2. 至瀏覽器輸入 IP:5000


* 更詳細操作步驟[請參閱HowHowWen官網](https://jeffwen0105.com/python-%E4%BD%BF%E7%94%A8flask-%E8%A3%BD%E4%BD%9C%E7%B0%A1%E5%96%AE%E7%9A%84%E7%99%BB%E5%85%A5%E5%8F%8A%E7%99%BB%E5%87%BA%E7%B6%B2%E7%AB%99/)


---

[![](https://i.imgur.com/sgdmN00.png)](https://buymeacoffee.com/jeffwen0105)
如果覺得內容還不錯，請我喝杯咖啡吧～