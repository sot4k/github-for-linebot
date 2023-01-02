from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import os


import pandas as pd

import time

from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def auth():
    SP_CREDENTIAL_FILE = 'secretkey.json'
    SP_SCOPE = [
        'https://spreadsheets.google.com/feeds', 
        'https://www.googleapis.com/auth/drive'
    ]
    SP_SHEET_KEY = '17gkxQa1jSWTNLBcsygTARoMX4T0rL1HODAI9auxJ3sY'
    SP_SHEET = 'timesheet' 

    credentials = ServiceAccountCredentials.from_json_keyfile_name(SP_CREDENTIAL_FILE, SP_SCOPE)
    gc = gspread.authorize(credentials)

    worksheet = gc.open_by_key(SP_SHEET_KEY).worksheet(SP_SHEET)
    return worksheet


#　開始
def punch_in():
    start_time = time.time()
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())

    timestamp = datetime.now()
    date = timestamp.strftime('%Y/%m/%d')
    punch_in = timestamp.strftime('%H:%M')

    data = [[date, punch_in, '00:00']]
    df1 = pd.DataFrame(data, columns = ['日付', '勉強開始時間', '勉強終了時間'])
    df = pd.concat([df, df1])
    
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

#　終了
def punch_out():
    elapsed_time = int(time.time() - start_time)
    elapsed_hour = elapsed_time // 3600
    elapsed_minute = (elapsed_time % 3600) // 60
    elapsed_second = (elapsed_time % 3600 % 60)
    
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())

    timestamp = datetime.now()
    punch_out = timestamp.strftime('%H:%M')

    df.iloc[-1, 2] = punch_out

    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    
    
    
app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = 'jjVn95fN2oKScGSAkgBPQHkldMEDFDeZR/finOubFVWnSiSYBswORQQV/JtBMlLF8qaHCdPieNuVE4mGGXY+EgE4ZOq8vLmgAg5o54nG09J/hXCt65cqG49dyxAkpg5I7bKWyboqRzWMucTvFs+ICAdB04t89/1O/w1cDnyilFU='
YOUR_CHANNEL_SECRET = 'd058ffa9941847ab9c17b2de3e99a55c'

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route("/")
def hello_world():
    return "hello world"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "開始":
        punch_in()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='さおが勉強はじめました！頑張れ！‼‼'))
        
    elif event.message.text == "終了":
        punch_out()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text={'勉強おわりました！お疲れさまでした！　勉強時間は、',str(elapsed_hour).zfill(2) + ":" + str(elapsed_minute).zfill(2) + ":" + str(elapsed_second).zfill(2),'でした！'}))
    


if __name__ == "__main__":
    port = os.getenv("PORT")
    app.run(host="0.0.0.0", port=port)