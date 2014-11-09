import os
import cgi
import urllib
import json

import webapp2
from google.appengine.ext.webapp import template
from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import users
from google.appengine.api import mail
import datetime

class Photo(db.Model):
  """Models an individual Photo entry with content and date."""
  content = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  avatar = db.BlobProperty()
  update = db.DateTimeProperty(auto_now=True)
  stream_name = db.StringProperty()
  author = db.StringProperty()
  Counter =  db.StringProperty() # The invokation times 
  history_views=  db.StringProperty()
  tag = db.StringProperty() 
  latitude =   db.StringProperty(default="")
  longitude =  db.StringProperty(default="")


class Sub(db.Model):
  """Models an sub entry connect one user to one stream"""
  stream_name = db.StringProperty()

class History(db.Model):
  """Models an view history to one stream"""
  stream_name = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)  

class CronJob(db.Model):
  """Models to store the cron job invocation frequency"""
  admin_name = db.StringProperty()
  Period =  db.IntegerProperty() # How many minutes between consecutive invokations 
  Counter =  db.IntegerProperty() # The invokation times 

def user_key(user_email=None):
  return db.Key.from_path('Photo', user_email or 'default_user_email')


def user_subkey(user_email=None):
  return db.Key.from_path('Sub', user_email or 'default_user_email')

def his_key():
  return db.Key.from_path('History', 'defaultkey')


def cron_key():
  return db.Key.from_path('CronJob', 'defaultkey')
  
# Covers for all streams
class MainPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      logout = users.create_logout_url('/')
      photos = (db.GqlQuery('SELECT * '
                            'FROM Photo '
                            'WHERE ANCESTOR IS :1 '
                            'ORDER BY update DESC, stream_name ASC',
                            user_key(user.email())))
      streams = []
      for one_photo in photos.run():
        if (((len(streams) == 0) or (one_photo.stream_name != streams[-1].stream_name)) and (one_photo.avatar!=None)):
          streams.append(one_photo)

      if len(streams)!=0:
	default_stream = streams[0].stream_name
      else:
	default_stream = "default_stream"
		

      subs = (db.GqlQuery('SELECT * '
                          'FROM Sub '
                          'WHERE ANCESTOR IS :1',
                          user_subkey(user.email())))
      sub_list = []
      for one_sub in subs.run():
        sub_list.append(one_sub.stream_name)
      photos = (db.GqlQuery('SELECT * '
                            'FROM Photo '
                            'WHERE stream_name IN :1 '
                            'ORDER BY update DESC, stream_name ASC',
                            sub_list))
      sub_streams = []
      for one_photo in photos.run():
        if (((len(sub_streams) == 0) or (one_photo.stream_name != sub_streams[-1].stream_name))):
          sub_streams.append(one_photo)
      # calculate the numbers in each string
      # prepare the context for the template
      context = {"photos": streams,
                 "logout": logout,
		"default_stream":default_stream,
      }
      
      # Create the cron jobs, by default the cron job will not be invoked
      crons = (db.GqlQuery('SELECT * '
                                'FROM CronJob '
                                'ORDER BY Period DESC'))
      crons_list = []
      for one_cron in crons.run():
          crons_list.append(one_cron)
      if len(crons_list)==0:# register a cron job if there is no cron job
	      cron_job = CronJob(parent=cron_key())
	      cron_job.Period = 0
	      cron_job.Counter = 0
	      cron_job.admin_name = user.email()
	      cron_job.put()

      

      # calculate the template path
      path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
      # render the template with the provided context
      self.response.out.write(template.render(path, context))

    else:
      self.redirect(users.create_login_url(self.request.uri))


# Info for all streams
class Manage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      logout = users.create_logout_url('/')
      photos = (db.GqlQuery('SELECT * '
                            'FROM Photo '
                            'WHERE ANCESTOR IS :1 '
                            'ORDER BY update DESC, stream_name ASC',
                            user_key(user.email())))
      streams = []
      for one_photo in photos.run():
        if ((len(streams) == 0) or (one_photo.stream_name != streams[-1].stream_name)):
          streams.append(one_photo)
      if len(streams)!=0:
	default_stream = streams[0].stream_name
      else:
	default_stream = "default_stream"



      subs = (db.GqlQuery('SELECT * '
                          'FROM Sub '
                          'WHERE ANCESTOR IS :1',
                          user_subkey(user.email())))
      sub_list = []
      for one_sub in subs.run():
        sub_list.append(one_sub.stream_name)
      photos = (db.GqlQuery('SELECT * '
                            'FROM Photo '
                            'WHERE stream_name IN :1 '
                            'ORDER BY update DESC, stream_name ASC',
                            sub_list))
      sub_streams = []
      for one_photo in photos.run():
        if ((len(sub_streams) == 0) or (one_photo.stream_name != sub_streams[-1].stream_name)):
	  if one_photo.avatar!=None:
           sub_streams.append(one_photo)
      # prepare the context for the template

      photos = (db.GqlQuery('SELECT * '
                            'FROM Photo '
                            'ORDER BY update DESC, stream_name ASC'
                            ))
      streams_pics = {}
      for one_photo in photos.run():
	if(one_photo.stream_name not in streams_pics.keys()):
		streams_pics[one_photo.stream_name]=0
	else:
		streams_pics[one_photo.stream_name]=streams_pics[one_photo.stream_name]+1
      for one_photo in streams:
	one_photo.Counter = str(streams_pics[one_photo.stream_name])
      for one_photo in sub_streams:
	one_photo.Counter = str(streams_pics[one_photo.stream_name])





      # calculate view times 
      ViewClick = (db.GqlQuery('SELECT * '
                                'FROM History '
                                'ORDER BY date DESC'))
      stream_views={}
      for  one_history in ViewClick.run():
	if one_history.stream_name not in stream_views.keys():
	  stream_views[one_history.stream_name] = 1
	else:
	  stream_views[one_history.stream_name] = stream_views[one_history.stream_name] + 1	
      for one_photo in streams:
	if one_photo.stream_name not in stream_views.keys():
		one_photo.history_views = str(0)
	else:
		one_photo.history_views = str(stream_views[one_photo.stream_name])
      for one_photo in sub_streams:
	if one_photo.stream_name not in stream_views.keys():
		one_photo.history_views = str(0)
	else:
		one_photo.history_views = str(stream_views[one_photo.stream_name])

      context = {"all_steams": streams,
                 "sub_streams": sub_streams,
                 "logout": logout,
		"default_stream":default_stream,
      }
      # calculate the template path
      path = os.path.join(os.path.dirname(__file__), 'templates', 'manage.html')
      # render the template with the provided context
      self.response.out.write(template.render(path, context))

    else:
      self.redirect(users.create_login_url(self.request.uri))


# All photos in current stream
class View(webapp2.RequestHandler):
  def get(self):

    user = users.get_current_user()
    if user:
      logout = users.create_logout_url('/')
      current_stream = str(self.request.get("current_stream"))
      if current_stream == None:
        current_stream = 'default stream'
      all_photos = (db.GqlQuery('SELECT * '
                                'FROM Photo '
                                'ORDER BY update DESC'))
      photos = []
      for one_photo in all_photos.run():
        if ((one_photo.stream_name == current_stream) and (one_photo.avatar!=None)):
          photos.append(one_photo)
        if len(photos) >= 3:
          break
      one_history = History(parent=his_key())
      one_history.stream_name=current_stream
      one_history.put() 
      context = {"photos": photos,
                 "current_stream": current_stream,
                 "logout": logout,
		"default_stream":current_stream,
      }
      # calculate the template path
      path = os.path.join(os.path.dirname(__file__), 'templates', 'view.html')
      # render the template with the provided context
      self.response.out.write(template.render(path, context))
    else:
      self.redirect(users.create_login_url(self.request.uri))

# All photos in current stream
class ViewAll(webapp2.RequestHandler):
  def get(self):

    user = users.get_current_user()
    if user:
      logout = users.create_logout_url('/')
      current_stream = self.request.get("current_stream")
      if current_stream == None:
        current_stream = 'default stream'
      all_photos = (db.GqlQuery('SELECT * '
                                'FROM Photo '
                                'ORDER BY update DESC'))
      photos = []
      for one_photo in all_photos.run():
        if ((one_photo.stream_name == current_stream) and (one_photo.avatar!=None)):
          photos.append(one_photo)
        if len(photos) >= 1000:
          break
      one_history = History(parent=his_key())
      one_history.stream_name=current_stream
      one_history.put() 
      context = {"photos": photos,
                 "current_stream": current_stream,
                 "logout": logout,
		"default_stream":current_stream,
      }
      # calculate the template path
      path = os.path.join(os.path.dirname(__file__), 'templates', 'viewAll.html')
      # render the template with the provided context
      self.response.out.write(template.render(path, context))
    else:
      self.redirect(users.create_login_url(self.request.uri))

# search
class Search(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      keyword=self.request.get("search_name")
      if keyword=='':
	keyword="The default"
      print keyword
    user = users.get_current_user()
    if user:
      logout = users.create_logout_url('/')
      all_photos = (db.GqlQuery('SELECT * '
                                'FROM Photo '
                                'ORDER BY update DESC, stream_name ASC'))
      subs = (db.GqlQuery('SELECT * '
                          'FROM Sub '
                          'WHERE ANCESTOR IS :1',
                          user_subkey(user.email())))
      sub_list = []
      for one_sub in subs.run():
        sub_list.append(one_sub.stream_name)
      streams = []


      default_stream = "default_stream"

      for one_photo in all_photos.run():
	default_stream = one_photo.stream_name
        if (((len(streams) == 0) or (one_photo.stream_name != streams[-1].stream_name)) and ((one_photo.author==user.email()) or (one_photo.stream_name in sub_list) )):
	 if one_photo.tag!=None and one_photo.avatar!=None:
          if(keyword in one_photo.tag):
            streams.append(one_photo)
      context = {"result_streams": streams,
                 "logout": logout,
		"default_stream":default_stream,
      }
      # calculate the template path

      path = os.path.join(os.path.dirname(__file__), 'templates', 'search.html')
      # render the template with the provided context
      self.response.out.write(template.render(path, context))
    else:
      self.redirect(users.create_login_url(self.request.uri))


class SubmitForm(webapp2.RequestHandler):
  def post(self):
    # We set the parent key on each 'Photo' to ensure each user's
    # photos are in the same entity group.
    user = users.get_current_user()
    RawImg = self.request.get("img")

    if RawImg == '':
      self.redirect('/error?msg=No image!')
    else:
      UpldContent = self.request.get("comments")
      ThumbImg = images.resize(RawImg, 500, 300)
      current_stream = str(self.request.get("current_stream"))
      #check if current user is author 
      photos = (db.GqlQuery('SELECT * '
                          'FROM Photo '
                          'WHERE stream_name = :1 '
                          'ORDER BY update DESC, stream_name ASC',
                          current_stream))
      check_photo=photos.get()
      if(check_photo.author==user.email()):
        one_photo = Photo(parent=user_key(user.email()))
        one_photo.content = self.request.get('comments')
        one_photo.avatar = db.Blob(ThumbImg)
        one_photo.stream_name = current_stream
        one_photo.author = user.email()
        one_photo.tag = check_photo.tag
        one_photo.latitude = ""
	one_photo.longitude = ""
        one_photo.put()
        self.redirect('/manage')
      else:
        self.redirect('/error?msg=Can only change your stream!')


class Image(webapp2.RequestHandler):
  def get(self):
    one_photo = db.get(self.request.get('img_id'))
    if one_photo.avatar:
      self.response.headers['Content-Type'] = 'image/png'
      self.response.out.write(one_photo.avatar)
    else:
      self.response.headers['Content-Type'] = 'text'
      self.response.out.write('No image')


class Create(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      logout = users.create_logout_url('/')

      photos = (db.GqlQuery('SELECT * '
                            'FROM Photo '
                            'WHERE ANCESTOR IS :1 '
                            'ORDER BY update DESC, stream_name ASC',
                            user_key(user.email())))
      streams = []
      for one_photo in photos.run():
        if (((len(streams) == 0) or (one_photo.stream_name != streams[-1].stream_name)) and (one_photo.avatar!=None)):
          streams.append(one_photo)
      if len(streams)!=0:
	default_stream = streams[0].stream_name
      else:
	default_stream = "default_stream"
      # calculate the template path
      path = os.path.join(os.path.dirname(__file__), 'templates', 'create.html')
      # render the template with the provided context
      context = {"logout": logout,
		 "default_stream":default_stream,
		}
      self.response.out.write(template.render(path, context))
    else:
      self.redirect(users.create_login_url(self.request.uri))


class SubmitStream(webapp2.RequestHandler):
  def post(self):
    # create a stream, with input of stream name, subscriber
    #let us first omit the tags optional message and cover
    user = users.get_current_user()
    current_stream = str(self.request.get("stream_name"))
    #check same stream name
    photos = (db.GqlQuery('SELECT * '
                            'FROM Photo '
                            'WHERE ANCESTOR IS :1 '
                            'ORDER BY update DESC, stream_name ASC',
                            user_key(user.email())))
    streams_name = []
    for one_photo in photos.run():
      if (((len(streams_name) == 0) or (one_photo.stream_name != streams_name[-1])) and (one_photo.avatar!=None)):
        streams_name.append(one_photo.stream_name)
    if current_stream in streams_name:
      self.redirect('/error?msg=The same stream name exist!')
    else:
      #raw_stream_name = self.request.get("stream_name")
      #current_stream = ''.join([line.strip() for line in raw_stream_name])  #processing the raw stream name
      email_list = self.request.get("email_list")
      tag = self.request.get("tag_name")
      optional_message = self.request.get("optional_message")
      #print "The stream name I am setting is: "
      #print current_stream
      sp_list=unicode.split(email_list)
      for one_email in sp_list:
        one_sub_entry = Sub(parent=user_subkey(one_email))
        one_sub_entry.stream_name=current_stream
        one_sub_entry.put()
        # send email
        sender_address = "" + user.nickname() + " <" + user.email() + ">"
        user_address = one_email
        subject = optional_message
        body = optional_message
        mail.send_mail(sender_address, user_address, subject, body)
      one_photo = Photo(parent=user_key(user.email()))
      one_photo.content = "This is fake photo represent a empty stream"
      one_photo.avatar = None
      one_photo.stream_name = current_stream
      one_photo.author = user.email()
      one_photo.tag=tag
      one_photo.put()
      one_photo.longitude=""
      one_photo.latitude=""
      self.redirect('/manage')


class DeleteStream(webapp2.RequestHandler):
  def post(self):
    # create a stream, with input of stream name, subscriber
    #let us first omit the tags optional message and cover
    user = users.get_current_user()
    checked_stream_names = self.request.get_all("stream_name")
    print "The stream name I am deleting is: "
    print checked_stream_names
    #print email_list
    #send email

    photos = (db.GqlQuery('SELECT * '
                          'FROM Photo '
                          'WHERE ANCESTOR IS :1 '
                          'ORDER BY update DESC, stream_name ASC',
                          user_key(user.email())))
    deleteKey = []
    for one_photo in photos.run():
      print one_photo.stream_name
      if ((one_photo.stream_name in checked_stream_names) ):
        deleteKey.append(one_photo.key())
    print deleteKey
    db.delete(deleteKey)

    self.redirect('/manage')



class UnsubscribeStream(webapp2.RequestHandler):
  def post(self):
    # create a stream, with input of stream name, subscriber
    #let us first omit the tags optional message and cover
    user = users.get_current_user()
    checked_stream_names = self.request.get_all("stream_name")
    print "The stream name I am deleting is: "
    print checked_stream_names
    #print email_list
    #send email

    photos = (db.GqlQuery('SELECT * '
                          'FROM Photo '
                          'WHERE ANCESTOR IS :1 '
                          'ORDER BY update DESC, stream_name ASC',
                          user_key(user.email())))
    deleteKey = []
    for one_photo in photos.run():
      print one_photo.stream_name
      if ((one_photo.stream_name in checked_stream_names) ):
        deleteKey.append(one_photo.key())
    print deleteKey
    db.delete(deleteKey)

    self.redirect('/manage')


class Trending(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      logout = users.create_logout_url('/')
      # Create the cron jobs, by default the cron job will not be invoked





      photos = (db.GqlQuery('SELECT * '
                            'FROM Photo '
                            'WHERE ANCESTOR IS :1 '
                            'ORDER BY update DESC, stream_name ASC',
                            user_key(user.email())))

      #retrieve all the stream names
      streams = []
      for one_photo in photos.run():
        if (((len(streams) == 0) or (one_photo.stream_name != streams[-1].stream_name)) and (one_photo.avatar!=None)):
          streams.append(one_photo)
      if len(streams)!=0:
	default_stream = streams[0].stream_name
      else:
	default_stream = "default_stream"

      #generate a dic where key=stream name:item=view times in the past hour
      ViewClick = (db.GqlQuery('SELECT * '
                                'FROM History '
                                'ORDER BY date DESC'))
      stream_views={}
      for  one_history in ViewClick.run():
	if one_history.stream_name not in stream_views.keys():
	  stream_views[one_history.stream_name] = 1
	else:
	  stream_views[one_history.stream_name] = stream_views[one_history.stream_name] + 1	  
      print stream_views.keys() 

      stream_view_stuple_list = []

      for one_photo in streams:
              if (one_photo.stream_name in stream_views.keys()):
		stream_view_stuple_list.append((stream_views[one_photo.stream_name], one_photo.stream_name))
	      else:
		stream_view_stuple_list.append((0, one_photo.stream_name))
      stream_view_stuple_list.sort(reverse=True)



      stream_covers = []
      streams_viewslist = []
      for i in range(min(len(stream_view_stuple_list),3)):
	for one_photo in streams:
	    if (one_photo.stream_name == stream_view_stuple_list[i][1]):
		  stream_covers.append(one_photo)
	streams_viewslist.append(stream_view_stuple_list[i][0])

      # Setting the highlight for cron job frequency options
      crons = (db.GqlQuery(     'SELECT * '
                                'FROM CronJob '
				"WHERE ANCESTOR IS :1 "
                                'ORDER BY Period DESC', cron_key()) )
      crons_list = []
      for one_cron in crons.run(read_policy=db.STRONG_CONSISTENCY, deadline=60 ):
          crons_list.append(one_cron)
      highlight_No = []
      highlight_5 = []
      highlight_10 = []
      highlight_60 = []

      if(len(crons_list)==0):
	highlight_No.append(0)
      else:
	if (crons_list[0].Period==0) : 
	  highlight_No.append(0)
	elif (crons_list[0].Period==5) : 
	  highlight_5.append(5)
	elif (crons_list[0].Period==10) : 
	  highlight_10.append(10)
	elif (crons_list[0].Period==60) : 
	  highlight_60.append(60)
      context = {"photos": stream_covers,
                 "logout": logout,
		 "streams_viewslist": streams_viewslist,
		"default_stream":default_stream ,
		"highlight_No": highlight_No,
		"highlight_5": highlight_5,      
		"highlight_10": highlight_10,      
		"highlight_60": highlight_60,
      }




      # calculate the template path
      path = os.path.join(os.path.dirname(__file__), 'templates', 'trending.html')
      # render the template with the provided context
      self.response.out.write(template.render(path, context))
  
    else:
      self.redirect(users.create_login_url(self.request.uri))


class SetCron(webapp2.RequestHandler):
  def post(self):
    # create a stream, with input of stream name, subscriber
    #let us first omit the tags optional message and cover
    user = users.get_current_user()
    rates = self.request.get_all("rate")
    print "The new rate is "
    print rates
    if len(rates)!=0:#One choice is made in the checkbox 
	    rate = rates[0]
	    crons = (db.GqlQuery('SELECT * '
		                        'FROM CronJob '
		                        'ORDER BY Period DESC'))
	    crons_list = []
	    # Delete the cron jobs
	    for one_cron in crons.run():
		crons_list.append(one_cron)
	    print crons_list
	    for one_cron in crons_list:
		db.delete(one_cron)
                print "deleting..."

	    # Create a cron job 
	    cron_job = CronJob(parent=cron_key())   
	    if rate == "No":
			cron_job.Period = 0
	    else:
			cron_job.Period = int(rate)
	    cron_job.Counter = 0
	    if len(crons_list)!=0:
	       cron_job.admin_name = crons_list[0].admin_name
	    cron_job.put();

    self.redirect('/trending')


class Cron(webapp2.RequestHandler):
  def get(self):

    # user = users.get_current_user()
    print "Debug for cron "



    # render the template with the provided context



    ViewClick = (db.GqlQuery('SELECT * '
                                'FROM History '
                                'ORDER BY date DESC'))

    history_list=[]
    history_toBeSent=[]
    for one_history in ViewClick.run():
      print (datetime.datetime.now() - one_history.date)
      print (datetime.datetime.now() - one_history.date)<datetime.timedelta(minutes=60)
      if((datetime.datetime.now() - one_history.date)>datetime.timedelta(minutes=60)): 
	 history_list.append(one_history)
      if((datetime.datetime.now() - one_history.date)<datetime.timedelta(minutes=60)): 
	 history_toBeSent.append(one_history)

    for one_history in history_list:
      db.delete(one_history)
      print "...Deleting history... "
      print one_history.date

    stream_views={}
    for  one_history in history_toBeSent:
	if one_history.stream_name not in stream_views.keys():
	  stream_views[one_history.stream_name] = 1
	else:
	  stream_views[one_history.stream_name] = stream_views[one_history.stream_name] + 1	  


    email_body = "";

    for key in stream_views.keys():
	email_body = email_body+"\""+key+"\""+" is viewed " + str(stream_views[key]) + " times in the past 1 hour"
	email_body = email_body+"\n"
    print email_body

    crons = (db.GqlQuery(     'SELECT * '
                                'FROM CronJob '
                                'ORDER BY Period DESC'))
    crons_list = []
    for one_cron in crons.run():
          crons_list.append(one_cron)
    if len(crons_list)!=0:# do the cron
	    for one_cron in crons_list:
		db.delete(one_cron)
                print "deleting..."
	    # Create a cron job 
	    cron_job = CronJob(parent=cron_key())   
	    cron_job.Period = crons_list[0].Period 
	    cron_job.Counter =  crons_list[0].Counter
	    cron_job.admin_name = crons_list[0].admin_name
	    if(cron_job.Period !=0):
		    if(cron_job.Counter >= cron_job.Period): 
			    cron_job.Counter = 0
			    user_nickname = "Tianhao and Zhuoran"
			    user_email = "zoranzhao@gmail.com"
			    email_list=["zoranzhao@gmail.com","zthzthzzz@gmail.com", "natviv@gmail.com", "ragha@utexas.edu"]
			    cron_job.put();
			    for one_email in email_list:
			      # send email
			      sender_address = "" + user_nickname + " <" + user_email + ">"
			      user_address = one_email
			      subject = "Report"
			      body = email_body
			      mail.send_mail(sender_address, user_address, subject, body)
	    
		    else:
			    cron_job.Counter = crons_list[0].Counter+1
			    cron_job.put();
	    else:
		cron_job.put();
		
class Error(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      logout = users.create_logout_url('/')
      msg = self.request.get("msg")

      photos = (db.GqlQuery('SELECT * '
                            'FROM Photo '
                            'WHERE ANCESTOR IS :1 '
                            'ORDER BY update DESC, stream_name ASC',
                            user_key(user.email())))

      #retrieve all the stream names
      streams = []
      for one_photo in photos.run():
        if (((len(streams) == 0) or (one_photo.stream_name != streams[-1].stream_name)) and (one_photo.avatar!=None)):
          streams.append(one_photo)
      if len(streams)!=0:
	default_stream = streams[0].stream_name
      else:
	default_stream = "default_stream"
      context = {"msg": msg,
                 "logout": logout,
		"default_stream":default_stream,
      }
      # calculate the template path
      path = os.path.join(os.path.dirname(__file__), 'templates', 'error.html')
      # render the template with the provided context
      self.response.out.write(template.render(path, context))
    else:
      self.redirect(users.create_login_url(self.request.uri))

class AndroidImage(webapp2.RequestHandler):
  def get(self):
    one_photo = db.get(self.request.get('img_id'))
    if one_photo.avatar:
      self.response.headers['Content-Type'] = 'image/png'
      self.response.out.write(one_photo.avatar)
    else:
      self.response.headers['Content-Type'] = 'text'
      self.response.out.write('No image')



class AndroidViewAllStreams(webapp2.RequestHandler):
  def get(self):
    #user = users.get_current_user()
    #if user:
      pos_name = -1
      pos = -1
      pos_response = self.request.get('pos')
      pos_name_response = self.request.get('pos_name')


      if pos_name_response!="":
        pos_name = int(pos_name_response)
      if pos_response!="":
      	pos = int(pos_response)

      photos = (db.GqlQuery('SELECT * '
                            'FROM Photo '
                            'ORDER BY update DESC, stream_name ASC'))
      streams = []
      for one_photo in photos.run():
        if (((len(streams) == 0) or (one_photo.stream_name != streams[-1].stream_name)) and (one_photo.avatar!=None)):
          streams.append(one_photo)
      streamThumJson = {}
      keyList=[]
      for photo in streams:
	streamThumJson[photo.stream_name] = str(photo.key())
	keyList.append(str(photo.key()))
      print streamThumJson
      if pos != -1:
	      if pos in range(len(keyList)):
		self.response.headers['Content-Type'] = 'image/png'
		one_photo = db.get(keyList[pos]);
		self.response.out.write(one_photo.avatar)
	      else:
		self.response.headers['Content-Type'] = 'text'
		self.response.out.write('')
      elif pos_name != -1:
	      if pos_name in range(len(keyList)):
		self.response.headers['Content-Type'] = 'text'
		one_photo = db.get(keyList[pos_name]);
		self.response.out.write(one_photo.stream_name)
	      else:
		self.response.headers['Content-Type'] = 'text'
		self.response.out.write('')
      #self.response.out.write(  json.dumps( keyList )  )
      #self.response.out.write( ( streamThumJson )  )
    #else:
    #  self.redirect(users.create_login_url(self.request.uri))

class AndroidViewAStream(webapp2.RequestHandler):
  def get(self):
      current_stream = self.request.get("current_stream")
      pos = int( self.request.get("pos") )
      getCount=self.request.get("get_count")
      all_photos = (db.GqlQuery('SELECT * '
                                'FROM Photo '
                                'ORDER BY update DESC'))
      photos = []
      for one_photo in all_photos.run():
        if ((one_photo.stream_name == current_stream) and (one_photo.avatar!=None)):
          photos.append(one_photo)
        if len(photos) >= 1000:
          break
      if getCount=="True":
	self.response.out.write(str(len(photos)))
      elif pos in range(len(photos)):
		self.response.headers['Content-Type'] = 'image/png'
		self.response.out.write(photos[pos].avatar)
      else:
		self.response.headers['Content-Type'] = 'text'
		self.response.out.write('')



class AndroidSearch(webapp2.RequestHandler):
  def get(self):
    username=str(self.request.get("user_name"))
    keyword=self.request.get("search_name")
    getCount=self.request.get("get_count")

    pos_name = -1
    pos = -1
    pos_response = self.request.get('pos')
    pos_name_response = self.request.get('pos_name')


    if pos_name_response!="":
        pos_name = int(pos_name_response)
    if pos_response!="":
      	pos = int(pos_response)


    all_photos = (db.GqlQuery('SELECT * '
                              'FROM Photo '
                              'ORDER BY update DESC, stream_name ASC'))
    subs = (db.GqlQuery('SELECT * '
                        'FROM Sub '
                        'WHERE ANCESTOR IS :1',
                        user_subkey(username)))
    sub_list = []
    for one_sub in subs.run():
      sub_list.append(one_sub.stream_name)
    streams = []


    default_stream = "default_stream"

    for one_photo in all_photos.run():
      default_stream = one_photo.stream_name
      if (((len(streams) == 0) or (one_photo.stream_name != streams[-1].stream_name)) and ((one_photo.author==username) or (one_photo.stream_name in sub_list) )):
       if one_photo.tag!=None and one_photo.avatar!=None:
        if(keyword in one_photo.tag) and keyword!="":
	  print "Key word is: "+keyword
	  print "Tag word is: "+one_photo.tag
          streams.append(one_photo)
    # The stream will contain all the photos with the correct tag.
    # Calculate the template path

    if getCount=="True":
	self.response.out.write(str(len(streams)))
    elif pos != -1:
	if pos in range(len(streams)):
		self.response.headers['Content-Type'] = 'image/png'
		self.response.out.write(streams[pos].avatar)
	else:
		self.response.headers['Content-Type'] = 'text'
		self.response.out.write('')
    elif pos_name != -1:
	if pos_name in range(len(streams)):
		self.response.headers['Content-Type'] = 'text'
		self.response.out.write(streams[pos_name].stream_name)
	else:
		self.response.headers['Content-Type'] = 'text'
		self.response.out.write('')

class AndroidUpload(webapp2.RequestHandler):
  def post(self):
    # We set the parent key on each 'Photo' to ensure each user's
    # photos are in the same entity group.
    latitude = self.request.get('latitude');
    longitude= self.request.get('longitude') ;

    current_stream = str(self.request.get("stream_name"))
    username=str(self.request.get("user_name"))

    #sender_address = username
    #user_address = username
    #subject = "Report"
    #body =     current_stream

    #mail.send_mail(sender_address, user_address, subject, body)

    RawImg = self.request.get("img")

    if RawImg == '':
      self.response.out.write('Error!')
    else:
      ThumbImg = images.resize(RawImg, 500, 300)

      #check if current user is author 
      photos = (db.GqlQuery('SELECT * '
                          'FROM Photo '
                          'WHERE stream_name = :1 '
                          'ORDER BY update DESC, stream_name ASC',
                          current_stream))
      check_photo=photos.get()
      if(check_photo.author==username):
        one_photo = Photo(parent=user_key(username))
        one_photo.content = self.request.get('comments')
        one_photo.avatar = db.Blob(ThumbImg)
        one_photo.stream_name = current_stream
        one_photo.author = username
        one_photo.tag = check_photo.tag
	one_photo.latitude = latitude
	one_photo.longitude = longitude
        one_photo.put()
    # username=str(self.request.get("user_name"))


class AndroidViewNearbyStreams(webapp2.RequestHandler):
  def get(self):
    #user = users.get_current_user()
    #if user:
      latitude = self.request.get('latitude');
      longitude= self.request.get('longitude') ;

      pos_name = -1
      pos = -1
      pos_response = self.request.get('pos')
      pos_name_response = self.request.get('pos_name')


      if pos_name_response!="":
        pos_name = int(pos_name_response)
      if pos_response!="":
      	pos = int(pos_response)

      photos = (db.GqlQuery('SELECT * '
                            'FROM Photo '
                            'ORDER BY update DESC, stream_name ASC'))
      streams = []
      for one_photo in photos.run():
        if (((len(streams) == 0) or (one_photo.stream_name != streams[-1].stream_name)) and (one_photo.avatar!=None)):
	  if(one_photo.latitude!="" and one_photo.longitude!="" ):
	    print one_photo.latitude
	    if ( abs (float(one_photo.latitude)-float(latitude)) + abs (float(one_photo.longitude)-float(longitude))  < 1 ):
             streams.append(one_photo)
      streamThumJson = {}
      keyList=[]
      for photo in streams:
	streamThumJson[photo.stream_name] = str(photo.key())
	keyList.append(str(photo.key()))
      print streamThumJson
      if pos != -1:
	      if pos in range(len(keyList)):
		self.response.headers['Content-Type'] = 'image/png'
		one_photo = db.get(keyList[pos]);
		self.response.out.write(one_photo.avatar)
	      else:
		self.response.headers['Content-Type'] = 'text'
		self.response.out.write('')
      elif pos_name != -1:
	      if pos_name in range(len(keyList)):
		self.response.headers['Content-Type'] = 'text'
		one_photo = db.get(keyList[pos_name]);
		self.response.out.write(one_photo.stream_name)
	      else:
		self.response.headers['Content-Type'] = 'text'
		self.response.out.write('')
      #self.response.out.write(  json.dumps( keyList )  )
      #self.response.out.write( ( streamThumJson )  )
    #else:
    #  self.redirect(users.create_login_url(self.request.uri))




application = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/error', Error),
  ('/view', View),
  ('/search', Search),
  ('/sign', SubmitForm),
  ('/createStream', SubmitStream),
  ('/deleteStream', DeleteStream),
  ('/unsubscribeStream', UnsubscribeStream),
  ('/manage', Manage ),
  ('/create', Create ),
  ('/trending', Trending ),  ('/trending/setCron', SetCron ),
  ('/img', Image),
  ('/cron/gatherStat', Cron),
  ('/viewAll',ViewAll ),
  ('/android/Image', AndroidImage),
  ('/android/ViewAllStreams', AndroidViewAllStreams),
  ('/android/ViewAStream', AndroidViewAStream),
  ('/android/search', AndroidSearch),
  ('/android/upload', AndroidUpload),
  ('/android/ViewNearbyStreams', AndroidViewNearbyStreams)
])
