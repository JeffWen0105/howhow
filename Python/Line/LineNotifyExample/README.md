###### tags: `Python`

# Python - Line Notify (含註冊教學) + Python API 串接



### Line Notify 使用步驟


0. 準備事項:
    1. 要有LINE帳號，註冊方式[請參考官網](https://line.me/zh-hant/account)
    2. LINE加入 Line Notify 官方帳號好友
    3. 註冊 Line Notify 服務


#### 加入 Line Notify 官方帳號好友

1. 搜尋好友輸入 @LineNotify 並加入官方帳號 
![](https://i.imgur.com/biO6VE5.png)
2. 建立可以接收訊息的群組並加入 Line Notify 官方帳號進入群內
![](https://i.imgur.com/daQknrv.png)




#### 註冊 Line Notify 服務

1. [登入官方Line notify網站](https://notify-bot.line.me/zh_TW/)


![](https://i.imgur.com/2SPM8xH.png)


2. 登入Line帳號


![](https://i.imgur.com/2DNbDHf.png)


3. 點選右上方帳號名稱，並選擇管理登錄服務

![](https://i.imgur.com/fBj2ghH.png)

4. 選擇登錄服務 (如果都沒有使用過相關服務，呈現空白很正常)


![](https://i.imgur.com/XzTuLn8.png)

5. 電子信箱請使用可以收認證信為主，其餘資料依個人喜好輸入


![](https://i.imgur.com/LHM1h0s.png)

6. 確認無誤後按下登錄

![](https://i.imgur.com/mwRpKri.png)

7. 至信箱收認證信後，點即前往服務一覽

![](https://i.imgur.com/v1TXHiO.png)

8. 屆時將出現Line Notify服務，並點選個人頁面


![](https://i.imgur.com/cNmMrn8.png)

9. 點擊發行權杖 

![](https://i.imgur.com/P2Rv9xv.png)

10. 依個人喜好設定機器人名稱，並選擇稍早建立好的接收訊息的群組

* 請確保Line Notify 官方帳號於選擇的群組內

![](https://i.imgur.com/TsRuOsp.png)

11. 複製權杖

![](https://i.imgur.com/T0SrkFk.png)

* 注意 !! 請確保權杖複製起來並儲存，不然會找不到該權杖

12. 創建 app.py 範例如下：

```python
import requests

def post_data(message, token):
    try:
        url = "https://notify-api.line.me/api/notify"
        headers = {
            'Authorization': f'Bearer {token}'
        }
        payload = {
            'message': message
        }
        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=payload
        )
        if response.status_code == 200:
            print(f"Success -> {response.text}")
    except Exception as _:
        print(_)

if __name__ == "__main__":
    token = "PSc1JOwORV46hYhU1kqcilmOAQJueRfipTGzfutD2lu" # 您的 Token
    message = "Example Post By HowHow Line Notify ~~"     # 要發送的訊息
    post_data(message, token)
```

13. 執行 python3 app.py

![](https://i.imgur.com/oaGwY4a.png)

14. 至 Line 群組上查看

![](https://i.imgur.com/dFGZmbj.png)


#### 上述步驟是不是非常簡單呢？？快點手刀操作創建自己的 Line 推播機器人八

* 相關程式碼可至 GitHub 下載，整包打包下載連結請點我

---

[![](https://i.imgur.com/sgdmN00.png)](https://buymeacoffee.com/jeffwen0105)
如果覺得內容還不錯，請我喝杯咖啡吧～