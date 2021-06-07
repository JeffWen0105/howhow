# 廣告成本自動寫入至神策工具

###  執行此程式會寫入 AdCost 事件，並附加廣告成本（亂數） 及廣告來源至神策指定的項目

#### 項目目錄說明

![](https://i.imgur.com/FntC5w6.png)


```
1. bin： python程式
2. conf： 程式設定組態檔
3. log : 程式日誌出位置
5. requirement.txt : python3 所需要的lib
6. start.sh 程式啟動入口
```

#### config.ini 設定組態檔說明

![](https://i.imgur.com/Sw9HkIw.png)


```

1. [XXXX] : 此項目為必填，請填入您的項目英文變數名稱，需用中刮號包住。

2. source : 廣告來源，可設定多個值，需使用逗號隔開（ ex. FB, Line, IG)。

3. amount_min: 廣告成本隨機亂數的下限值 （如寫入非數值形態，會自動轉化為 3,000，低於 1不會降低) 。

4. amount_max: 廣告成本隨機亂數的上限值 （如寫入非數值形態，會自動轉化為 10,000，超過 10,000,000不會增加)。
```




#### 程式執行方式

```
1. 請使用python3以上版本
2. 執行前先使用 pip3 install -r requirements.txt --no-index ，安裝所需lib
3. 配置導入工具組態檔
4. 執行 sh start.sh 導入的項目
ps. 可選參數： -t 自定義時間 ， -d 啟動debug模式，數據不會寫入
```

![](https://i.imgur.com/WtbKe14.png)


#### 執行範例

![](https://i.imgur.com/Hejy9Jf.png)


