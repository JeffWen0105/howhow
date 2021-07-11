from flask import Flask, render_template, request, Response, abort, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

def setToken():
        f = open(f'conf/token.txt', 'r')
        token = f.read()
        Token = token
        f.close()
    return Token

def push_video(num):
    Token = setToken
    with open(f"rawdata/video.json" , 'r') as reader:
        items = json.loads(reader.read())
    try:
        requests.post(
        url='https://notify-api.line.me/api/notify',
        headers={
            'Authorization': f'Bearer {Token}'
        },
        data={'message': f"\n銀魂第{num}集~\n{items[num]}",
                })
    except Exception as e:
        print(e)


def get_video_list():
    with open(f"output/video.json", 'r') as reader:
        data = json.loads(reader.read())
    return data

class Videos(Resource):
    def get(self):
        videos_list = get_video_list()
        return {"Data": {"Message": "Get an item", "Output": videos_list}}, 200


class GetVideo(Resource):
    def post(self, gid):
        try:
            push_video(gid)
            return {"Data": {"Message": "ok"}}, 200
        except Exception as e:
            return {"Data": {"Message": e}}, 401



api.add_resource(Videos, '/videos')
api.add_resource(GetVideo, '/getvideo/<string:gid>')