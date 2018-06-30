from LineTimeline import TimelineClient
from Objects import *
import sqlite3

#ログインしたクッキーを食べる
Cookie = 'INPUT_YOUR_COOKIE'
UserID = 'INPUT_USER_ID'
tcl = TimelineClient(Cookie)

#DB作成
conn = sqlite3.connect("%s.db"%(UserID))
create_table = '''create table posts (id INTEGER PRIMARY KEY AUTOINCREMENT, postId int, createdTime text, text text, likeCount int, commentCount int, photos text, videos text, stickers text, gps text, link text, readPermission text, sharedCount)'''
conn.execute(create_table)

#ダウンロード開始
tcl.get_user_posts(UserID,conn)
conn.close()
print("SAVE Complete")