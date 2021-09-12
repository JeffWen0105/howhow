# 使用Flask 製作簡單的登入（出）網頁

#### 使用說明:

```
1. 方案一 ： 預設方式啟動 Web，需自備 MySQL 及訪問權限
2. 方案二 ： 預設方式啟動 Web ，及使用 HowHow 建置的 Database Docker 容器
3. 方案三 ： 全部都使用 HowHow DB 及 Web 容器
```

### 方案一：

#### 0. 下載相關Python套件:

pip install -r requirements.txt

* 如沒有 GCC 或是 mysql-client 的 lib 需先安裝

#### 1. 創建SQL表

```
    /* MySQL */
	create table users ( id int not null auto_increment, name varchar(20) not null, email varchar(20) not null, password char(80) not null, primary key (id) );
```


#### 2. 修改程式碼內MySQL的登入帳號、密碼、資料庫名稱、資料庫IP:

```
	# ex. Python:
	app.config['MYSQL_HOST'] = '127.0.0.1'          # 登入ip
	app.config['MYSQL_USER'] = 'root'               # 登入帳號
	app.config['MYSQL_PASSWORD'] = 'root'           # 登入密碼
	app.config['MYSQL_DB'] = 'db'                   # 登入資料庫名稱
```

4. 執行程式方式

```
	 python3 app.py
```

5. 至瀏覽器輸入 IP:5000


注: 
	1. 請確保MySQL可以正常運作
	2. 更詳細操作步驟[請參閱HowHowWen官網](https://jeffwen0105.com/python-%E4%BD%BF%E7%94%A8flask-%E8%A3%BD%E4%BD%9C%E7%B0%A1%E5%96%AE%E7%9A%84%E7%99%BB%E5%85%A5%E5%8F%8A%E7%99%BB%E5%87%BA%E7%B6%B2%E7%AB%99/)


---

### 方案二：

* 需具備 Docker 及 Docker-compose ， [安裝方式請參閱HowHow官網](https://jeffwen0105.com/dokcer-%e8%b2%a8%e6%ab%83%e5%ae%b9%e5%99%a8%e5%85%a9%e4%b8%89%e4%ba%8b/)

#### 0. 



