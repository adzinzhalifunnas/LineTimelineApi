class ReadPermission(object):
    """
    Attributes:
     - type "ALL" "FRIEND" "NONE"
     - gids タイムラインgid(グループgidは不可)
    """
    def __init__(self,type="FRIEND",gids=[]):
        self.type = type
        self.gids = gids

class Sticker(object):
    """
    Attributes:
     - id スタンプ識別ID(long)
     - packageId スタンプID(short)
     - packageVersion 1(固定?)
    """
    def __init__(self,id=13854393,packageId=1347491,packageVersion="1"):
        self.id = id
        self.packageId = packageId
        self.packageVersion = packageVersion
        
class Media(object):
    """
    Attributes:
     - objectId オブジェクトID
     - type "VIDEO" / "PHOTO"
     - width
     - height
     - obsNamespace "tmp"?
     - serviceName "myhome"
     - obsFace "[]" ?
    """
    def __init__(self,objectId=None,type="PHOTO",width=500,height=500,obsNamespace="tmp",serviceName="myhome",obsFace="[]"):
        self.objectId = objectId
        self.type = type
        self.width = width
        self.height = height
        self.obsNamespace = obsNamespace
        self.serviceName = serviceName
        self.obsFace = obsFace

class Thumbnail(object):
    """
    Attributes:
     - url URL
     - width 横幅px(自動も可)
     - height 縦幅px(自動も可)
     - requiredTid false/True (???)
    """
    def __init__(self,url=None,width=None,height=None,requiredTid=None):
        self.url = url
        self.width = width
        self.height = height
        self.requiredTid = requiredTid
        
class Recall(object):
    """
    Attributes:
     - start テキスト内の何文字目からか(@の位置)
     - mid タイムラインmid(ユーザーmidは不可)
     - displayText ユーザー名(何を入れても自動で正しいものに修正される)
    """
    def __init__(self,start=None,mid=None,displayText="ゆら"):
        self.start = start
        self.mid = mid
        self.displayText = displayText

class Location(object):
    """
    Attributes:
     - name 地名
     - longtude 経度
     - latitude 緯度
     - thumbnail　サムネイル型(width height 必須 / urlはGoogleMapのビューワにあたる / WEBからのみ反映?)
    """
    def __init__(self,name="ちばけんま",longitude=139.988985,latitude=35.795379,thumbnail=None):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.thumbnail = thumbnail
        
class TextStyle(object):
    """
    Attributes:
     - textSizeMode
        "AUTO" デフォルト
        "LARGE" 大きくする(アニメ不可)
     - textAnimation
        "NONE" デフォルト
        "SLIDE"　左へ流れる
        "BUZZ"　揺れる
        "ZOOM" 奥から拡大
        "BOUNCE"　落ちてきて跳ねる
        "BLINK" 点滅
     - backgroundColor HTMLカラー(#ffffff,#000000...)
    """
    def __init__(self,textSizeMode="AUTO",textAnimation="ZOOM",backgroundColor="#000000"):
        self.textSizeMode = textSizeMode
        self.textAnimation = textAnimation
        self.backgroundColor = backgroundColor
        
class MediaStyle(object):
    """
    Attributes:
        -displayType "SLIDE"
    """
    def __init__(self,displayType="SLIDE"):
        self.displayType = displayType
        
class StickerStyle(object):
    """
    Attributes:
        -backgroundColor HTMLカラー
    """
    def __init__(self,backgroundColor="#000000"):
        self.backgroundColor = backgroundColor

class Link(object):
    """
    Attributes:
     - title ページ名　(これだけでも送れる)
     - main 説明文 (これだけでも送れる)
     - sub 表示されるリンク (これだけだとスルーされる)
     - url リンク (無しでも送れる) (これだけだとスルーされる)
     - thumburl サムネイルリンク(無しでも送れる) (これだけだとスルーされる/ タイトルに空白入れて誤魔化し可能)
     - obsthumbnail　obsサーバー内サムネデータ(無しでも送れる) (これだけだとスルーされる)
    """
    def __init__(self,title=None,main=None,sub=None,url=None,thumburl=None,obsthumbnail=None):
        self.title = title
        self.main = main
        self.url = url
        self.sub = sub
        self.thumburl = thumburl
        self.obsthumbnail = obsthumbnail

class Music(object):
    """
    Attributes:
     - title 曲名
     - artist 作曲者
     - sub LINE MUSIC
     - thumburl サムネリンク
     - musicid 音楽IDの文字列型
     - region "JP"等のリスト型
    """
    def __init__(self,title=None,artist=None,sub="LINE MUSIC",thumburl="http://tn.smilevideo.jp/smile?i=32372971",musicid="",region=["JP"]):
        self.title = title
        self.artist = artist
        self.sub = sub
        self.thumburl = thumburl
        self.musicid = musicid
        self.region = region

class Post(object):
    """
    Attributes:
     - readPermission　readPermission型
     - holdingTime int型
     - sharePostId int/str型
     - text str型
     - textMeta Recall型
     - stickers Sticker型
     - media Media型
     - mediaStyle MediaStyle型
     - textStyle TextStyle型
     - stickerStyle StickerStyle型
     - locations Location型
     - additionalContents Link型かMusic型
    """
    def __init__(self, readPermission=ReadPermission(), holdingTime=None,sharePostId=None,text="幼女食べたい", textMeta=[], stickers=[], media=[], mediaStyle=None, textStyle=None, stickerStyle=None, locations=None, additionalContents=None):
        self.readPermission = readPermission
        self.holdingTime = holdingTime
        self.sharePostId = sharePostId
        self.text = text
        self.textMeta = textMeta
        self.stickers = stickers
        self.media = media
        self.mediaStyle = mediaStyle
        self.textStyle = textStyle
        self.stickerStyle = stickerStyle
        self.locations = locations
        self.additionalContents = additionalContents