import web
web.config.debug = False
import os
import sqlite3
from replit import db
import requests
import json
import ast
import marko
from datetime import datetime

urls = (
	'/', 'index',
	'/(.*)/(.*)', "blog",
	'/edit', 'edit',
	'/edit2', 'edit2',
	'/delete', 'delete',
	'/new', 'new',
	'/login', 'login', 
	'/signup', 'signup',
	'/visibility', 'vis2',
	'/vis', 'vis',
	'/(.*)', 'user'
)

render = web.template.render('templates/')
app = web.application(urls, locals())
session = web.session.Session(app, web.session.DiskStore('sessions'))


class index:
	def GET(self):
		if not session.get("user"):
			return render.promo()
		else:
			user = session.get("user")
			titles = {}
			titles2 = requests.get("https://blogpool-titles.coolcodersj.repl.co/all").json()
			users = requests.get("https://blogpool-users.coolcodersj.repl.co/all").json()
			for title in titles2:
				for user2 in users:
					if title == user2 and users[user2] == user:
						titles[titles2[title]] = title
			
			i = web.input(code=0)
			msg = ""
			if i.code == "1":
				msg = "Blog edited successfully!"
			elif i.code == "2":
				msg = "Blog deleted successfully!"
			return render.index(user, titles, msg)
			

class login:
	def GET(self):
		##os.system("clear")	
		return render.login()
		##os.system("clear")	
		 
	def POST(self):
		##os.system("clear")	
		i = web.input()
		r = requests.post("https://sjauth.coolcodersj.repl.co/apil", data={"user":i.user, "passw":i.passw, "cn":"MasterBlogger"})
		print(r.text)
		if r.text == "True":
			session.user = i.user
			raise web.seeother("/")
		else:
			raise web.seeother("/login?code=1")
		##os.system("clear")	
		 

class signup:
	def GET(self):
		##os.system("clear")	
		return render.signup()
		##os.system("clear")	
		 
	def POST(self):
		##os.system("clear")	
		i = web.input()
		r = requests.post("https://sjauth.coolcodersj.repl.co/apisi", data={"user":i.user, "passw":i.passw, "cn":"MasterBlogger"})
		if r.text == "True":
			session.user = i.user
			raise web.seeother("/")
		else:
			raise web.seeother("/signup?code=1")
		##os.system("clear")	


class new:
	def GET(self):
		return render.new()
	def POST(self):
		i = web.input()
		db2 = []
		for key in db:
			db2.append(int(key))
		db2.sort(reverse=True)
		print(db2)
		if db2 == []:
			id = 1
		else:
			id = str(int(db2[0])+1)
		print(id, int(db2[0]))
		blog = i.blog
		db[str(id)] = blog
		now = datetime.now()
		tim = now.strftime("%d/%m/%Y %H:%M")
		user = session.get("user")
		requests.post("https://blogpool-users.coolcodersj.repl.co/set", data={"key":str(id), "val": user, 'AUTH':os.getenv("AUTH")})
		requests.post("https://blogpool-titles.coolcodersj.repl.co/set", data={"key":str(id), "val":i.title, 'AUTH':os.getenv("AUTH")})
		requests.post("https://blogpool-times.coolcodersj.repl.co/set", data={"key":str(id), "val":tim, 'AUTH':os.getenv("AUTH")})
		if "type"  not in i  or  i.type == "Public":
			requests.post("https://blogpool-types.coolcodersj.repl.co/set", data={"key":str(id), "val":"public"})
		elif i.type == "Unlisted":
			requests.post("https://blogpool-types.coolcodersj.repl.co/set", data={"key":str(id), "val":"unlisted"})
		elif i.type == "Draft":
			requests.post("https://blogpool-types.coolcodersj.repl.co/set", data={"key":str(id), "val":"draft"})
		raise web.seeother(f"/{user}/{id}")

class edit:
	def POST(self):
		i = web.input()
		title = requests.get(f"https://blogpool-titles.coolcodersj.repl.co/key/{str(i.id)}").text
		return render.edit(db[str(i.id)], title, i.id)

class edit2:
	def POST(self):
		i = web.input()
		db[str(i.id)] = i.blog
		print()
		requests.post("https://blogpool-titles.coolcodersj.repl.co/set", data={"key":str(i.id), "val":i.title, 'AUTH':os.getenv("AUTH")})
		print()
		raise web.seeother("/?code=1")

class vis2:
	def POST(self):
		i = web.input()
		return render.vis(i.id)

class vis:
	def POST(self):
		i = web.input()
		requests.post("https://blogpool-types.coolcodersj.repl.co/set", data={"key":str(i.id), "val":i.type.lower(), 'AUTH':os.getenv("AUTH")})
		print()
		user = session.get("user")
		raise web.seeother(f"/{user}/{i.id}")

class delete:
	def POST(self):
		i = web.input()
		id = i.id
		requests.post("https://blogpool-users.coolcodersj.repl.co/delete", data={"key":str(id), 'AUTH':os.getenv("AUTH")})
		requests.post("https://blogpool-titles.coolcodersj.repl.co/delete", data={"key":str(id), 'AUTH':os.getenv("AUTH")})
		requests.post("https://blogpool-times.coolcodersj.repl.co/delete", data={"key":str(id), 'AUTH':os.getenv("AUTH")})
		requests.post("https://blogpool-types.coolcodersj.repl.co/delete", data={"key":str(id), 'AUTH':os.getenv("AUTH")})
		del db[str(id)]
		raise web.seeother("/?code=2")

class user:
	def GET(self, user):
		if "/" not in user:
			raise web.seeother(f"/{user}/")
		else:
			raise web.seeother(f"/{user}")

class blog:
	def GET(self, user, id=None):
		if id != '':
			datuser = requests.get(f"https://blogpool-users.coolcodersj.repl.co/key/{str(id)}").text
			visibility = requests.get(f"https://blogpool-types.coolcodersj.repl.co/key/{str(id)}").text
			if user != datuser or (visibility  == "draft" and user != session.get("user")):
				return render.notfound()
			content = marko.convert(db[str(id)])
			creation_time = requests.get(f"https://blogpool-times.coolcodersj.repl.co/key/{str(id)}").text
			title = requests.get(f"https://blogpool-titles.coolcodersj.repl.co/key/{str(id)}").text
			if visibility != "public":
				badge = '<mark class="alert text" style="margin-left: 15px; padding: 10px;">'+visibility.title()+'</mark>'
			else:
				badge = ""
			return render.blog(user, creation_time, content, title, badge)
		else:
			titles = {}
			titles2 = requests.get("https://blogpool-titles.coolcodersj.repl.co/all").json()
			users = requests.get("https://blogpool-users.coolcodersj.repl.co/all").json()
			vis = requests.get("https://blogpool-types.coolcodersj.repl.co/all").json()
			for title in titles2:
				for user2 in users:
					if title == user2 and users[user2] == user:
						if vis[title] ==  'public':
							titles[titles2[title]] = title
			return render.user(titles, user)



if __name__ == "__main__":
	app.run()
