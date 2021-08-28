# 自動取得 Line UID 系統


#### Line UUID 是不是一個唯一值呢？其實只能算答對一半，Line UUID 僅對同一個 Bot Channel 才會是唯一值，那如果是自己新創建 Channel 的 BOT ，就透過此系統可以自動抓出使用者 ID 、 群組 ID 及聊天室 ID ， 不需在另外寫 Code 及部屬至 Server 上了～

### 使用方式 （ 特別是第三點，需注意 ）

#### 1. 登入 howhow 的 [GetLineID](https://lineuid.howhow.tk) 網站。

![](https://i.imgur.com/nC3PkbE.png)


#### 2. 至 [ LINE Developers ](https://developers.line.biz/) 平台查看 Token 及 Secret


* Secret 查看如下

![](https://i.imgur.com/cvYE0b3.png)

* Token 查看如下

![](https://i.imgur.com/8aIxnD5.png)




#### 3. 確保 WebHook 已經開啟， 如果 WebHook URL 為空值（ 本身沒有接過 server )，可以透過輸入``` https://example.com ``` 該網址並且 update ， 且不需進行驗證，另請打開下方的 Use webhook 功能 ！！ （ 務必啟用該功能 ）


![](https://i.imgur.com/ygIAr40.png)



#### 4. 至 howhow 網站， 點擊右上角的 Setting 並輸入相關資訊。


![](https://i.imgur.com/0oRvv6M.png)

#### 5. 確認輸入無誤，點擊驗證，如通過將有 5 分鐘時間 可以透過該系統查詢 Line Uid。

![](https://i.imgur.com/CqiL2Cg.png)


#### 6. 至Line 輸入 myid （不區分大小寫） 或是點擊圖文選單 （ 群組及聊天室無此功能 ）

* DEMO 01 如下

![](https://i.imgur.com/YbRhb91.png)

* DEMO 02 如下

![](https://i.imgur.com/xNcsYln.png)

* DEMO 03 如下

![](https://i.imgur.com/mIjyzx3.png)


#### 7. 點擊右上角的 Detail 可以查看目前該系統有沒有人使用中，並顯示租借到期時間。

![](https://i.imgur.com/oKkOyPW.png)




##### PS. 本系統程式碼均開源，可以至 HowHow 的 GitHub 下載原始碼

[整包下載請點擊我](https://downgit.github.io/#/home?url=https://github.com/JeffWen0105/howhow/tree/main/Python/Line/getLineUid)


---



[![](https://i.imgur.com/sgdmN00.png)](https://buymeacoffee.com/jeffwen0105)
如果覺得內容還不錯，請我喝杯咖啡吧～