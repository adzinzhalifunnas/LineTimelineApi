from LineTimeline import TimelineClient
from Objects import *

Cookie = 'INPUT_YOUR_COOKIE'
tcl = TimelineClient(Cookie)
post = Post()
post.text = "Hello world"
tcl.postTimeline(post)