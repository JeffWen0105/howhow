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