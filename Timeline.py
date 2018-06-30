# coding: utf-8
import http.client,urllib.parse,re,os,requests,time,math
import urllib.request as urllib
import json,zlib,time,random
from datetime import datetime
import base64
from time import sleep
from bs4 import BeautifulSoup
from collections import OrderedDict
from Objects import *

class TimelineClient():
    headers = {
        'User-Agent':'',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ja,en-US;q=0.8,en;q=0.6',
        'X-Timeline-WebVersion': '',
        'X-Line-AcceptLanguage': 'ja',
        'Content-Type':'application/json;charset=UTF-8',
        'Referer':'https://timeline.line.me/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Origin': 'https://timeline.line.me',
        'Cookie': ''}
    decoder = json.JSONDecoder(object_pairs_hook=OrderedDict)
    #headersの指定
    def __init__(self,cookie,ver='',ua=''):
        self.conn = http.client.HTTPSConnection('timeline.line.me')
        self.headers['X-Timeline-WebVersion'] = str(ver)
        self.headers['Cookie'] = str(cookie)
        self.headers['User-Agent'] = str(ua)

    #今後似たようなの書くのがめんどいので
    def req(self,type,addr,body=''):
        body = body.encode('utf8')
        self.conn.request(type, "/api/"+addr, body, self.headers)
        return self.conn.getresponse()

    #if status == 200: return True else: return False って書くのがめんどいので
    def isOK(self,code):
        if code == 200:
            return True
        else:
            return False
    
    #めんどくさがり屋のため。
    def getHomeID(self,text):
        return text[text.find("post/")+5:text.find("/",text.find("post/")+5)]
    #めんどくさがり屋のため。
    def getPostID(self,text):
        return text[text.find("/",text.find("post/")+5)+1:]
        
    '''
    スクラップのレスポンス
        NOTE: 存在しなかったリンク情報は "" として返される
        {
            "code": 0,
            "message": "success",
            "result": {
                "url": "http://line.me",
                "domain": "line.me",
                "title": "LINE : Free Calls & Messages",
                "summary": "LINE is a new communication app which allows you to make FREE voice calls and send FREE messages whenever and wherever you are, 24 hours a day!",
                "ogUrl": "https://line.me/en-US/",
                "updated": "2017-12-09 14:08:36",
                "image": "/r/scrap/s/c3RhdGljLmxpbmUubmF2ZXIuanA9b577bb3",
                "obs": {
                    "sid": "s",
                    "oid": "c3RhdGljLmxpbmUubmF2ZXIuanA9b577bb3",
                    "hash": "0hW_SqZyy4CHBuCCQ8-gR3J1FKBAMTeVFkTDxFdRJdIB0YRRNvEz0bcg9bCjdAUyZeFj4YZkNbUkZFaxwk",
                    "service_code": "scrap"
                },
                "video": {
                    "hours": 0,
                    "minutes": 0,
                    "seconds": 0
                },
                "redirected": "https://line.me/en-US/",
                "isvideo": false,
                "image_source": "http://static.line.naver.jp/line_lp/img/ogimage.png",
                "image_width": 1500,
                "image_height": 1500,
                "line_id": "",
                "line_title": "",
                "line_message": "",
                "line_image_source": ""
            }
        }
    '''
    #スクラップ(サーバーにリンク情報を保存)する (動作しない)
    def Scrap(self,url):
        ur = urllib.parse.urlencode({'url':url,'caller':'TIMELINE_WEB'})
        resp = requests.get('https://timeline.line.me/scrap/api/v2/pageinfo/get.json?'+ur,headers=self.headers)
        js = resp.text.json()["result"]
        return js

    def now_milliseconds(self):
        return int(time.time() * 1000)
        
    def date_time_milliseconds(self,date_time_obj):
        return int(time.mktime(date_time_obj.timetuple()) * 1000)

    
    #画像をサーバーに投稿する
    def postImage(self,path):
        pass
    
    #投稿にいいねする(0ならランダムで選ぶ)
    #1 love 2 haha 3 ok 4 terharu 5 kaget 6 cry 0 random
    def likePost(self,post_id,homeid,reaction=0,sharable=False):
        if reaction not in [0,1,2,3,4,5,6] : return "ERROR: Invalid reaction id!"
        if reaction == 0: reaction = random.randint(1,6)
        if sharable == True: sharable = 'true'
        else: sharable = 'false'
        body = '{"contentId":"'+str(post_id)+'","actorId":"'+str(homeid)+'","likeType":"100'+str(reaction)+'","sharable":'+sharable+'}'
        if homeid == self.myid:
            to = 'like/create.json?sourceType=MYHOME&homeId='
        else:
            to = 'like/create.json?sourceType=TIMELINE&homeId='
        resp = self.req('POST',to+str(homeid),body)
        return self.isOK(resp.status)
    
    #投稿のいいねをキャンセルする
    def unlikePost(self,post_id):
        body = '{"contentId":"'+str(post_id)+'"}'
        resp = self.req('POST','like/cancel.json?sourceType=TIMELINE&homeId=x',body)
        return self.isOK(resp.status)
    
    #投稿にコメントする
    def commentPost(self,post_id,home_id,comment_text):
        body = '{"contentId":"'+str(post_id)+'","commentText":"'+str(comment_text)+'","contentsList":[],"actorId":"'+str(home_id)+'","recallInfos":[]}'
        resp = self.req('POST','comment/create.json?sourceType=MYHOME&homeId='+str(home_id),body)
        return self.isOK(resp.status)
    
    #投稿へのコメントを削除する
    def deleteComment(self,post_id,home_id,comment_id):
        body = '{"postId":"'+str(post_id)+'","actorId":"'+str(home_id)+'","commentId":"'+str(comment_id)+'"}'
        resp = self.req('POST','comment/delete.json?sourceType=MYHOME&homeId='+str(home_id))
        return self.isOK(resp.status)
    
    #ハッシュタグで検索して結果を取得する
    def searchByHashtag(self,hashtag="profile",limit=10):
        resp = self.req('GET','hashtag/search.json?query='+hashtag+'&postLimit='+str(limit)+'&commentLimit=1&likeLimit=1')
        if self.isOK(resp.status):
            ret = json.loads(zlib.decompress(resp.read(), 16+zlib.MAX_WBITS).decode('utf8'))
            return ret["result"]
        else:
            return "ERROR:"+str(resp.status)

    #ユーザー情報を取得する(仕様変更で死亡?)
    def userinfo(self):
        resp = self.req('GET','gnb/userInfo.json')
        if self.isOK(resp.status):
            ret = json.loads(zlib.decompress(resp.read(), 16+zlib.MAX_WBITS).decode('utf8'))
            return ret["result"]
        else:
            return "ERROR:"+str(resp.status)
            
    #グループリストを取得する
    def groupList(self,limit=1000):
        resp = self.req('GET','group/list.json?limit='+str(limit))
        if self.isOK(resp.status):
            ret = json.loads(zlib.decompress(resp.read(), 16+zlib.MAX_WBITS).decode('utf8'))
            return ret["result"]
        else:
            return "ERROR:"+str(resp.status)
    
    #グループ名からgidを取得する
    def getGidByName(self,name):
        grs = self.groupList()["groups"]
        for group in grs:
            if name in grs[group]["name"]:
                return grs[group]["groupId"]
        return "Not found"
    
    #グループ情報を取る
    def getGroup(self,gid,postLimit=10,commentLimit=2,likeLimit=10):
        resp = self.req('GET','post/list.json?homeId='+gid+'&postLimit='+str(postLimit)+'&commentLimit='+str(commentLimit)+'&likeLimit='+str(likeLimit)+'&requestTime=1513275483894')
        return resp["result"]
            
    #通知一覧を取得する
    def notification(self):
        resp = self.req('GET','gnb/noticenter.json')
        if self.isOK(resp.status):
            ret = json.loads(zlib.decompress(resp.read(), 16+zlib.MAX_WBITS).decode('utf8'))
            return ret["result"]["notifications"]
        else:
            return "ERROR:"+str(resp.status)
    
    #タイムラインに投稿する(PostObjectを投げる)
    def postTimeline(self,data,rawdata=None):
        #テンプレート
        pd = OrderedDict()
        pd["postInfo"] = OrderedDict()
        pd["postInfo"]["readPermission"] = OrderedDict()
        pd["postInfo"]["readPermission"]["type"] = "FRIEND"
        pd["postInfo"]["readPermission"]["gids"] = None
        pd["postInfo"]["holdingTime"] = None
        pd["contents"] = OrderedDict()
        pd["contents"]["text"] = " "
        pd["contents"]["textMeta"] = []
        pd["contents"]["stickers"] = []
        pd["contents"]["media"] = []
        pd["contents"]["contentsStyle"] = OrderedDict()
        pd["contents"]["contentsStyle"]["mediaStyle"] = {}
        pd["contents"]["contentsStyle"]["textStyle"] = {}
        pd["contents"]["contentsStyle"]["stickerStyle"] = {}
        pd["contents"]["locations"] = []
        #削除までの時間
        if data.holdingTime != None:
            pd["postInfo"]["holdingTime"] = data.holdingTime
        #投稿共有
        if data.sharePostId != None:
            pd["postInfo"]["sharePostId"] = str(data.sharePostId)
            pd["contents"]["sharedPostId"] = str(data.sharePostId)
            pd["contents"].pop("locations")
        #閲覧範囲
        if data.readPermission != None:
            if type(data.readPermission) == ReadPermission:
                pd["postInfo"]["readPermission"]["type"] = data.readPermission.type
                if data.readPermission.gids != []:
                    pd["postInfo"]["readPermission"]["gids"] = data.readPermission.gids
            else:
                raise TypeError("Must be ReadPermission Type")
        #テキスト
        if data.text != None:
            pd["contents"]["text"] = data.text
        #メンション
        if data.textMeta != []:
            for i in range(0,len(data.textMeta)):
                pd["contents"]["textMeta"].append({"type":"RECALL","start": data.textMeta[i].start,"end": data.textMeta[i].start+1,"mid": data.textMeta[i].mid,"displayText":data.textMeta[i].displayText,"bold": False,"url": {"type": "INTERNAL","targetUrl": "#HOME"}})
        #スタンプ
        if data.stickers != []:
            for i in range(0,len(data.stickers)):
                pd["contents"]["stickers"].append({"id":data.stickers[i].id,"packageId":data.stickers[i].packageId,"packageVersion":data.stickers[i].packageVersion})
        #画像と動画
        if data.media != []:
            for i in range(0,len(data.media)):
                medo = OrderedDict()
                medo["objectId"] = data.media[i].objectId
                oidX = data.media[i].objectId
                medo["type"] = data.media[i].type
                medo["width"] = data.media[i].width
                medo["height"] = data.media[i].height
                medo["obsNamespace"] = data.media[i].obsNamespace
                medo["serviceName"] = data.media[i].serviceName
                medo["obsFace"] = data.media[i].obsFace
                pd["contents"]["media"].append(medo)
        #画像と動画の表示方法
        if data.mediaStyle != None:
            pd["contents"]["contentsStyle"]["mediaStyle"] = {"displayType":data.mediaStyle.displayType}
        #テキスト表示方法
        if data.textStyle != None:
            if type(data.textStyle) == TextStyle:
                pd["contents"]["contentsStyle"]["textStyle"] = {"textSizeMode":data.textStyle.textSizeMode,"textAnimation":data.textStyle.textAnimation,"backgroundColor":data.textStyle.backgroundColor}
            else:
                raise TypeError("Must be TextStyle Type")
        #スタンプ表示方法
        if data.stickerStyle != None:
            pd["contents"]["contentsStyle"]["stickerStyle"] = {"backgroundColor":data.stickerStyle.backgroundColor}
        #位置情報
        if data.locations != None:
            if type(data.locations) == Location:
                pd["contents"]["locations"] = [{"name":data.locations.name,"longitude":data.locations.longitude,"latitude":data.locations.latitude}]
            else:
                raise TypeError("Must be Location Type")
        #URL / LINE Music
        if data.additionalContents != None: 
            pd["additionalContents"] = {}
            if type(data.additionalContents) == Music:
                pd["additionalContents"]["url"] =  {"type": "WEB","targetUrl": "LINE MUSIC"}
                pd["additionalContents"]["title"] = data.additionalContents.title
                pd["additionalContents"]["main"] = data.additionalContents.artist
                pd["additionalContents"]["sub"] = data.additionalContents.sub
                pd["additionalContents"]["obsthumbnail"] = {"width": 130,"height": 130,"preferCdn": True,"resourceId": "hTvuAtMjCF1gQVARWKgIQISgmVWlhCE8Lcl1BOmk5VWhsDk8KfFhBPGRtVTk1CUoGcl1AaGo7VToyCUhafApBPjlsV29mWh5YfVgTOWw"}
                pd["additionalContents"]["thumbnail"] = {"width": None,"height": None,"requiredTid": False,"url":data.additionalContents.thumburl}
                pd["additionalContents"]["music"] = {"type":"mt","regions":data.additionalContents.region,"id":data.additionalContents.musicid}
            elif type(data.additionalContents) == Link:
                pd["additionalContents"]["url"] =  {"type": "WEB","targetUrl": data.additionalContents.url}
                pd["additionalContents"]["title"] = data.additionalContents.title
                pd["additionalContents"]["main"] = data.additionalContents.main
                if data.additionalContents.sub != None:
                    pd["additionalContents"]["sub"] = data.additionalContents.sub
                else:
                    pd["additionalContents"]["sub"] = data.additionalContents.url
                if data.additionalContents.thumburl != None:
                    pd["additionalContents"]["thumbnail"] = {"url":data.additionalContents.thumburl,"width":None,"height":None}
                if data.additionalContents.obsthumbnail != None:
                    pd["additionalContents"]["obsthumbnail"] = data.additionalContents.obsthumbnail
            else:
                raise TypeError("The type for additionalContents must be Music or Link")
        pd = json.dumps(pd).replace(" ","")
        if rawdata == None:
            print(pd)
        else:
            pd = rawdata
        print("Sending")
        resp = self.req('POST','post/create.json?sourceType=HASHTAG_SEARCH',pd)
        print("Sent")
        print(zlib.decompress(resp.read(), 16+zlib.MAX_WBITS).decode('utf8'))
        return self.isOK(resp.status)
        
    #投稿を共有する
    def sharePost(self,postid):
        srp = Post(text=None)
        srp.sharePostId = postid
        self.postTimeline(srp)
    #投稿を削除する
    def deletePost(self,postid,homeid):
        body = '{"postId":"'+postid+'"}'
        resp = self.req('POST','post/delete.json?sourceType=TIMELINE&homeId='+str(homeid),body)
        return self.isOK(resp.status)

    #HomeIDから友達追加する
    #homeid = ブラウザからアクセスするリンクに含まれるホームID
    #stringでmessageを返すのでそれで判断してください
    def addFriend(self,homeid):
        body = '{"mid":"'+homeid+'"}'
        resp = self.req('POST',"friend/add.json",body)
        resp = str(resp.read().decode("utf-8"))
        resp = json.loads(resp)
        return resp["message"]
    
    #スクロールしたければ scrollId=21 のように nextScrollIdを付けて再要求
    #友達一覧を取得する
    def friendList(self):
        resp = self.req('GET','friend/list.json?limit=1000')
        if self.isOK(resp.status):
            ret = json.loads(zlib.decompress(resp.read(), 16+zlib.MAX_WBITS).decode('utf8'))
            return ret
        else:
            return "ERROR:"+str(resp.status)
    
    #ユーザー名からMidを取得する
    def getFriendMidByName(self,name):
        ids = self.friendList()["result"]["friends"]
        for user in ids:
            if name in ids[user]["displayName"]:
                return ids[user]["mid"]
        return "Not found"

    #ステータスメッセージからMidを取得する
    def getFriendMidByStatus(self,status):
        ids = self.friendList()["result"]["friends"]
        for user in ids:
            if status in ids[user]["statusMessage"]:
                return ids[user]["mid"]
        return "Not found"
    
    #特定の人の投稿数を確認する。
    def chk_posts(self,homeid):
        bt = int(time.time())*1000
        resp = self.req('GET','post/list.json?homeId='+homeid+'&postLimit=10&commentLimit=2&likeLimit=20&requestTime='+str(bt))
        resp = json.loads(zlib.decompress(resp.read(), 16+zlib.MAX_WBITS).decode('utf8'))
        #print("投稿数は"+str(resp["result"]["homeInfo"]["postCount"])+"個")
        return resp["result"]["homeInfo"]["postCount"]
            
    #特定の投稿のコメント数を確認する。
    def chk_postComments(self,homeid,postid):
        resp = self.req('GET',"comment/getList.json?homeId="+str(homeid)+"&contentId="+str(postId)+"&limit=10")
        resp = json.loads(zlib.decompress(ret.read(), 16+zlib.MAX_WBITS).decode('utf8'))
        print("  コメントは"+str(ret["result"]["commentCount"])+"個")
        return resp["result"]["commentCount"]
    
    #特定の投稿のいいね数を確認する。
    def chk_postLikes(self,homeid,postid):
        resp = self.req('GET',"like/getList.json?sourceType=MYHOME&contentId="+str(postId)+"&actorId="+str(homeid))
        resp = json.loads(zlib.decompress(ret.read(), 16+zlib.MAX_WBITS).decode('utf8'))
        body = resp.read()
        try:
            resp = json.loads(body.decode('utf8'))
        except:
            resp = json.loads(zlib.decompress(body, 16+zlib.MAX_WBITS).decode('utf8'))
        print("  いいねは"+str(resp["result"]["allLikes"]["likeCount"])+"個")
        return resp["result"]["allLikes"]["likeCount"]
    
    #特定の投稿のjsonを取得する
    def getPost(self,homeid,postid):
        html = urllib.urlopen("https://timeline.line.me/post/"+str(homeid)+"/"+str(postid))
        soup = BeautifulSoup(html,"lxml")
        soup.find_all("script",text=re.compile("window.__PRELOADED_STATE__"))
        data = soup.text
        return json.loads(data[data.find("window.__PRELOADED_STATE__ =")+28:])

    #特定の投稿の内容を取得する
    def getText(self,json_data):
        return json_data["postEnd"]["feed"]["post"]["contents"]["text"]
        
    #特定の投稿のupdatedTimeを取得する
    def getUpdatedTime(self,json_data):
        return json_data["postEnd"]["feed"]["post"]["postInfo"]["updatedTime"]
    
    #特定の投稿のcreatedTimeを取得する    
    def getCreatedTime(self,json_data):
        return json_data["postEnd"]["feed"]["post"]["postInfo"]["createdTime"]
        
    #特定の投稿の投稿に共有された回数を取得する
    def getSharedToPost(self,json_data):
        return json_data["postEnd"]["feed"]["post"]["postInfo"]["sharedCount"]["toPost"]
        
    #特定の投稿のトークに共有された回数を取得する
    def getSharedToTalk(self,json_data):
        return json_data["postEnd"]["feed"]["post"]["postInfo"]["sharedCount"]["toTalk"]
        
    def getPosts(self,homeid,nextId):
        tri = 0
        while True:
            try:
                tri+=1
                bt = int(time.time())*1000
                if nextId != None:
                    resp = self.req('GET','post/list.json?homeId=%s&postLimit=10&commentLimit=2&likeLimit=20&scrollId=%s&requestTime=%s'%(homeid,nextId,bt))
                else:
                    resp = self.req('GET','post/list.json?homeId=%s&postLimit=10&commentLimit=2&likeLimit=20&requestTime=%s'%(homeid,bt))
                ret = json.loads(zlib.decompress(resp.read(), 16+zlib.MAX_WBITS).decode('utf8'))["result"]
                break
            except:
                try:
                    print("ERROR")
                    x = resp.read()
                    print(x)
                    print(zlib.decompress(x, 16+zlib.MAX_WBITS).decode('utf8'))
                except:
                    pass
                sleep(random.randint(20+(tri*2),30+(tri*3)))
        return ret
    #このままだとIDがあてにならない問題がある...
    def get_user_posts(self,homeid,conn,start=0,end=1000000):
        c = conn.cursor()
        insert_sql = """insert into posts (postId, createdTime, text, likeCount, commentCount, photos, videos, stickers, gps, link, readPermission, sharedCount)
                        values (?,?,?,?,?,?,?,?,?,?,?,?)"""
        nextId = None
        numi = 1
        datas = []
        while nextId != "":
            posts = []
            data = self.getPosts(homeid,nextId)
            print("%s Page Got_OK"%(numi))
            numi += 1
            if numi > start and numi < end+2 and "feeds" in data:
                for feed in data["feeds"]:
                    post = []
                    # postId
                    post.append(feed["post"]["postInfo"]["postId"])
                    # createdTime (3桁削る 0を消す)
                    post.append(str(datetime.fromtimestamp(int(str(feed["post"]["postInfo"]["createdTime"])[:-3]))))
                    # text
                    if "text" in feed["post"]["contents"]:
                        post.append(feed["post"]["contents"]["text"])
                    elif "additionalContents" in feed["post"]:
                        if "main" in feed["post"]["additionalContents"]:
                            if feed["post"]["additionalContents"]["main"] == "プロフィールを変更しました!":
                                post.append("プロフィールを変更しました!")
                            else:
                                post.append(None)
                        else:
                            post.append(None)
                    else:
                        post.append(None)
                    # likeCount
                    post.append(feed["post"]["postInfo"]["likeCount"])
                    # commentCount
                    post.append(feed["post"]["postInfo"]["commentCount"])
                    # media
                    if "media" in feed["post"]["contents"]:
                        phs = []
                        vds = []
                        for m in feed["post"]["contents"]["media"]:
                            if m["type"] == "PHOTO" or m["type"] == "ANIGIF":
                                phs.append(m["resourceId"])
                            elif m["type"] == "VIDEO":
                                vds.append(m["resourceId"])
                            else:
                                print(m["type"])
                                x = input('>> EXCEPT <<')
                        # photos
                        post.append(','.join(phs))
                        # videos
                        post.append(','.join(vds))
                    else:
                        # photos
                        post.append(None)
                        # videos
                        post.append(None)
                    # stickers
                    if "stickers" in feed["post"]["contents"]:
                        sts = []
                        for s in feed["post"]["contents"]["stickers"]:
                            sts.append(str({"id":s["id"],"packageId":s["packageId"],"packageVersion":s["packageVersion"]}))
                        post.append(",".join(sts))
                    else:
                        post.append(None)
                    # gps
                    if "locations" in feed["post"]["contents"]:
                        lcs = []
                        for l in feed["post"]["contents"]["locations"]:
                            #場所名があるかどうか
                            if "poiInfo" in l:
                                if l["poiInfo"] != None:
                                    lcs.append(str({"name":l["name"],"placeName":l["poiInfo"]["placeName"],"longitude":l["longitude"],"latitude":l["latitude"],"thumbnail":l["thumbnail"]["url"]}))
                                else:
                                    lcs.append(str({"name":l["name"],"longitude":l["longitude"],"latitude":l["latitude"],"thumbnail":l["thumbnail"]["url"]}))
                            else:
                                lcs.append(str({"name":l["name"],"longitude":l["longitude"],"latitude":l["latitude"],"thumbnail":l["thumbnail"]["url"]}))
                        post.append(",".join(lcs))
                    else:
                        post.append(None)
                    # link
                    if "additionalContents" in feed["post"]:
                        d = feed["post"]["additionalContents"]
                        link = {}
                        if "title" in d: link["title"] = d["title"]
                        if "main" in d: link["main"] = d["main"]
                        if "sub" in d: link["sub"] = d["sub"]
                        if "obsthumbnail" in d: link["thumbnail"] = d["obsthumbnail"]["resourceId"]
                        if "url" in d:
                            if "targetUrl" in d["url"]: link["url"] = d["url"]["targetUrl"]
                        post.append(str(link))
                    else:
                        post.append(None)
                    # readPermission
                    post.append(feed["post"]["postInfo"]["readPermission"]["type"])
                    # sharedCount
                    if "sharedCount" in feed["post"]["postInfo"]:
                        post.append(str(feed["post"]["postInfo"]["sharedCount"]))
                    else:
                        post.append(None)
                    # add
                    posts.append(tuple(post))
                nextId = data["nextScrollId"]
                c.executemany(insert_sql, posts)
                sleep(random.randint(1,4))
            else:
                if "feeds" not in data: break
                if numi > end: break
                sleep(1)
        conn.commit()
    
    '''
    HomeIDから投稿を全て取得する(通常はページ数を指定するが -1が飛んできたらすべてを一括で落とす(BAN注意!!) )
    　homeid = ブラウザからアクセスするリンクに含まれるホームID
     例:
      https://timeline.line.me/api/post/list.json?homeId=XXXX&postLimit=10&commentLimit=2&likeLimit=20&requestTime=1500650528918
    '''
    def getHomelist(self,homeid=None,pages=5,order="TIME",start_from=-1):
        if pages == -1: pages = 10000
        #return用
        result = {}
        #投稿個数カウント用
        post_cnt = 0
        #pagesの指定回数繰り返す
        for i in range(0,pages):
            if i > start_from:
                sleep(random.randint(1,1))
            #エポック時間
            #nextId = "1150787574701087054_1507875747000"
            bt = int(time.time())*1000
            if i == 0:
                #初回取得
                if homeid == None:
                    #友達全員のタイムラインの最新ページ
                    resp = self.req('GET','feed/list.json?postLimit=10&commentLimit=2&likeLimit=20&order='+order+'&requestTime='+str(bt))
                else:
                    #特定の人のタイムラインの最新ページ
                    resp = self.req('GET','post/list.json?homeId='+homeid+'&postLimit=10&commentLimit=2&likeLimit=20&requestTime='+str(bt))
            else:
                #2回目以降の取得
                if homeid == None:
                    #友達全員のタイムラインの次のページ
                    resp = self.req('GET','feed/list.json?postLimit=10&commentLimit=2&likeLimit=20&order='+order+'&scrollId='+nextId+'&requestTime='+str(bt))
                else:
                    #特定の人のタイムライン
                    if i == 1:
                        nextId = "1150787574701087054_1507875747000"
                    resp = self.req('GET','post/list.json?homeId='+homeid+'&postLimit=10&commentLimit=2&likeLimit=20'+'&scrollId='+nextId+'&requestTime='+str(bt))
                    print('post/list.json?homeId='+homeid+'&postLimit=10&commentLimit=2&likeLimit=20'+'&scrollId='+nextId+'&requestTime='+str(bt))
            if self.isOK(resp.status):
                print (str(i+1)+"ページ目の取得に成功") 
                #どこに入れるかの参照用
                pi = 0
                #処理が最初かどうか
                cli = 0
                resp_body = json.loads(zlib.decompress(resp.read(), 16+zlib.MAX_WBITS).decode('utf8'))
                if i == 0:
                    if 'officialHome' in resp_body['result']['homeInfo']:
                        official = True
                    else:
                        official = False
                if i > start_from:
                    try:
                        #投稿毎に処理する/コメントを取得して追加する部分
                        for post in resp_body["result"]["feeds"]:
                            post_cnt+=1
                            #コメント処理部分
                            try:
                                nextId = post["post"]["comments"]["nextScrollId"]
                            except:
                                nextId = ""
                            old_nextId = ""
                            postId = post["feedInfo"]["id"]
                            #print(" "+str(post_cnt)+"個目の投稿の処理を開始します")
                            #print(" "+"https://timeline.line.me/api/comment/getList.json"+"?homeId="+str(homeid)+"&contentId="+str(postId)+"&scrollId="+str(nextId)+"&limit=10")
                            if nextId != "":
                                #次のコメント一覧を取得する
                                while True:
                                    if cli != 0:
                                        ret = self.req('GET',"comment/getList.json"+"?homeId="+str(homeid)+"&contentId="+str(postId)+"&scrollId="+str(nextId)+"&limit=10")
                                    else:
                                        ret = self.req('GET',"comment/getList.json"+"?homeId="+str(homeid)+"&contentId="+str(postId)+"&limit=10")
                                    get = ret.read()
                                    try:
                                        ret = json.loads(zlib.decompress(get, 16+zlib.MAX_WBITS).decode('utf8'))
                                    except:
                                        ret = json.loads(get.decode('utf8'))
                                    for data in ret["result"]["commentList"]:
                                        #コメントの追加　コメント一覧にdataが入っていなければ実行
                                        if data not in resp_body["result"]["feeds"][pi]["post"]["comments"]["commentList"]:
                                            comi = 0
                                            add = True
                                            #同一のコメントIDのコメントがないか確認し、あればそれのlikeCountを書き換え、
                                            #なければ追加する。
                                            for comment in resp_body["result"]["feeds"][pi]["post"]["comments"]["commentList"]:
                                                if comment["commentId"] == data["commentId"]:
                                                    add = False
                                                    resp_body["result"]["feeds"][pi]["post"]["comments"]["commentList"][comi]["likeCount"] = data["likeCount"]
                                                comi+=1
                                            if add == True:
                                                resp_body["result"]["feeds"][pi]["post"]["comments"]["commentList"].append(data)
                                    nextId = ret["result"]["nextScrollId"]
                                    #print("Comment_Next: "+str(nextId))
                                    #ここが怪しい！(コメントがちゃんと2回以上取れるように修正すること！)
                                    if type(nextId) != str:
                                        break
                                    else:
                                        cli+=1
                                        if old_nextId == nextId:break
                                        old_nextId = nextId
                                #print("  コメントは"+str(ret["result"]["commentCount"])+"個")
                            #else:
                                #print("  コメントがありませんでした。")
                            #いいね処理部分
                            try:
                                nextId2 = post["post"]["likes"]["nextScrollId"]
                            except:
                                nextId2 = ""
                            if nextId2 != "":
                                reg = self.req('GET',"like/getList.json?sourceType=MYHOME&contentId="+str(postId)+"&actorId="+str(homeid)+"&scrollId="+str(nextId2))
                                #一度しか読めない疑惑
                                body = reg.read()
                                try:
                                    #ここで一度読んじゃうと
                                    reg = json.loads(body.decode('utf8'))
                                except:
                                    #ここで読む時点で中身がなくなる
                                    reg = json.loads(zlib.decompress(body, 16+zlib.MAX_WBITS).decode('utf8'))
                                #print("  いいねは"+str(reg["result"]["allLikes"]["likeCount"])+"個")
                                if reg["result"]["allLikes"]["likeCount"] > 12:
                                    while True:
                                        for data in reg["result"]["allLikes"]["likeList"]:
                                            if data not in resp_body["result"]["feeds"][pi]["post"]["likes"]["likeList"]:
                                                resp_body["result"]["feeds"][pi]["post"]["likes"]["likeList"].append(data)
                                        if official == True:
                                            print("　公式アカウントのため一覧取得はできません。")
                                            break
                                        if reg["result"]["allLikes"]["existNext"] == False:
                                            break
                                        else:
                                            nextId2 = reg["result"]["allLikes"]["nextScrollId"]
                                            reg = self.req('GET',"like/getList.json?sourceType=MYHOME&contentId="+str(postId)+"&actorId="+str(homeid)+"&scrollId="+str(nextId2))
                                            #一度しか読めない疑惑
                                            body = reg.read()
                                            try:
                                                #ここで一度読んじゃうと
                                                reg = json.loads(body.decode('utf8'))
                                            except:
                                                #ここで読む時点で中身がなくなる
                                                reg = json.loads(zlib.decompress(body, 16+zlib.MAX_WBITS).decode('utf8'))
                                            #print("　もう1周行って!")
                            #else:
                                #print("  いいねがありませんでした")
                            pi+=1
                    except:
                        try:
                            print(resp_body)
                        except:
                            pass
                        print("取得失敗のため強制終了します。")
                        return result["result"]
                if i == 0:
                    result = resp_body
                else:
                    for data in resp_body["result"]["feeds"]:
                        result["result"]["feeds"].append(data)
                #print (resp_body["result"]["feeds"][0]["feedInfo"]["id"])
                if i < pages:
                    nextId = resp_body["result"]["nextScrollId"]
                else:
                    print("指定ページ到達")
                    return result["result"]
                #よくわからんから移動
                '''
                if len(resp_body["result"]["feeds"]) != 10:
                    if i == 0:
                        result = resp_body
                    print("最終ページ到達")
                    return result["result"]
                '''
            else:
                return result["result"]
        return result["result"]
    
    #Jsonデータから全画像/動画 をダウンロードする。
    def getHomeDatas(self,json_data):
        #フォルダを用意する
        try:
            main_f = "./"+str(json_data["homeInfo"]["userInfo"]["mid"])+"_"+str(json_data["homeInfo"]["userInfo"]["nickname"])
            if os.path.exists(main_f) == False:
                os.mkdir(main_f)
            time_f = datetime.now().strftime("%y%m%d%H%M%S")
            print(time_f)
            os.mkdir(main_f+"/"+str(time_f))
        except:
            print("フォルダ作成失敗")
            return "Failed"
        #ファイルを取得しまくる
        f_cnt = 0
        for post in json_data["feeds"]:
            f_cnt+=1
            print(str(f_cnt)+"個目の投稿")
            if "media" in post["post"]["contents"]:
                for data in post["post"]["contents"]["media"]:
                    get_link = "https://obs.line-scdn.net/"+str(data["resourceId"])
                    print(get_link)
                    try:
                        with urllib.urlopen(get_link) as response:
                            result = response.info()
                            print("FileType: "+result["Content-Type"])
                            if result["Content-Type"] == "image/jpeg":
                                ext = ".jpg"
                            elif result["Content-Type"] == "video/mp4":
                                ext = ".mp4"
                            elif result["Content-Type"] == "image/gif":
                                ext = ".gif"
                            elif result["Content-Type"] == "application/octet-stream":
                                ext = ".jpg"
                            else:
                                return "Error"
                            with open(main_f+"/"+str(time_f)+"/"+data["resourceId"]+ext,"wb") as f:
                                f.write(response.read())
                    except:
                        print("取得できなかったためダミーを保存しました")
                        with open(main_f+"/"+str(time_f)+"/"+data["resourceId"]+".404","w") as f:
                                f.write("Not Found.")    
                    sleep(random.randint(1,3))
            else:
                print("データがありませんでした。")
        print("Complete")
        return True
        
    def getCommentDatas(self,json_data):
        #フォルダを用意する
        try:
            main_f = "./"+str(json_data["homeInfo"]["userInfo"]["mid"])+"_"+str(json_data["homeInfo"]["userInfo"]["nickname"])
            if os.path.exists(main_f) == False:
                os.mkdir(main_f)
            time_f = datetime.now().strftime("%y%m%d%H%M%S")
            print(time_f)
            os.mkdir(main_f+"/"+str(time_f))
        except:
            print("フォルダ作成失敗")
            return "Failed"
        #ファイルを取得しまくる
        f_cnt = 0
        for post in json_data["feeds"]:
            f_cnt+=1
            print(str(f_cnt)+"個目の投稿")
            if "comments" in post["post"] and f_cnt > 600:
                for comment in post["post"]["comments"]["commentList"]:
                    if "contentsList" in comment and comment["contentsList"] != None:
                        for conts in comment["contentsList"]:
                            if conts["extData"] != None:
                                if "resourceId" in conts["extData"]:
                                        get_link = "https://obs.line-scdn.net/"+str(conts["extData"]["resourceId"])
                                        print(get_link)
                                        try:
                                            with urllib.urlopen(get_link) as response:
                                                result = response.info()
                                                print("FileType: "+result["Content-Type"])
                                                if result["Content-Type"] == "image/jpeg":
                                                    ext = ".jpg"
                                                elif result["Content-Type"] == "video/mp4":
                                                    ext = ".mp4"
                                                elif result["Content-Type"] == "image/gif":
                                                    ext = ".gif"
                                                else:
                                                    return "Error"
                                                with open(main_f+"/"+str(time_f)+"/"+conts["extData"]["resourceId"]+ext,"wb") as f:
                                                    f.write(response.read())
                                        except:
                                            print("取得できなかったためダミーを保存しました")
                                            with open(main_f+"/"+str(time_f)+"/"+conts["extData"]["resourceId"]+".404","w") as f:
                                                    f.write("Not Found.")    
                                        sleep(random.randint(1,3))
        print("Complete")
        return True
    '''
    新規投稿を取得する？
    
    Referer からページは判別？
    https://timeline.line.me/api/feed/newfeed.json?
    requestTime=1500651236844
    {code: 0, message: "success", result: {,…}}
    '''
    def getNewfeed(self):
        pass