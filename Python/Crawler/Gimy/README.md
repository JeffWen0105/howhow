# Gimy 劇迷影片網站爬蟲工具

#### ~~~~ Source Code 打包下載[請點我](https://downgit.github.io/#/home?url=https://github.com/JeffWen0105/howhow/tree/main/Python/Crawler/Gimy) ~~~~

### 透過此工具可以將有[Gimy 劇迷](https://gimy.one/)上動漫等多個影片源下載為json檔，供後續線上播放使用

#### 項目目錄說明

```
1. bin： python程式
2. conf： 爬蟲設定組態檔
3. log : 程式日誌輸入位置
4. output: 預設輸出檔案的位置
5. requirement.txt : python3 所需要的lib
6. start.sh 程式啟動入口
```

#### conf 設定組態檔說明
```
1. video_id : 此項目為必填，如何查看video_id位置如下圖
```
![](https://i.imgur.com/QlBW00c.jpg)
```
2. file_path : 自定義要輸出的 路徑 + 檔名 ，如未添加路徑檔案會輸出在bin內！！

3. limit : 爬取的集數，請勿超過預設爬取的集數

```

#### 程式執行方式
```
1. 請使用python3以上版本
2. 執行前先使用 pip3 install -r requirements.txt --no-index ，安裝所需lib
3. 配置爬蟲組態檔
4. 執行 sh start.sh

* 注：此程式設定爬取多集數影片，如僅需爬取一部請自行修改程式碼，如下圖
```
![](https://i.imgur.com/Du9Jc17.png)


<font size="1"><I><b>注： 此工具僅供教學用途，請於下載影片連結後24小時內刪除，請勿用於商業目的；若有版權問題，使用者必須自行負責。</b></I></font>
