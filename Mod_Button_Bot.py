import praw
import time
from collections import deque
import re
import os

#initialize reddit
r=praw.Reddit(user_agent="Toolbox Button Bot alpha /u/captainmeta4")

#set globals
username = "Mod_Button_Bot"
password = os.environ.get('password')

caching_subreddit="Mod_Button_Bot_Log"

permissions_fail = "I wasn't able to complete the requested action. I do not have the necessary moderator permissions."



class Bot(object):

    def load_caches(self):
        #load already-processed comments cache and modlist cache
        try:
            self.cache = eval(r.get_wiki_page(caching_subreddit,"comment_cache").content_md)
            print("comment cache loaded")
            
        except:
            print("comment cache not loaded. Starting with blank cache")
            self.cache = deque([],maxlen=1000)

        try:
            self.modlist = eval(r.get_wiki_page(caching_subreddit,"modlist_cache").content_md)
            print("modlist cache loaded")
        except:
            print("modlist cache not loaded. Reloading all moderator lists")
            self.modlist = {}
            self.update_moderators()

    def login_bot(self):

        print("logging in...")
        r.login(username, password)
        print("success")

    def do_comments(self):

        print("processing comments")
        
        acted_this_cycle=False
        
        for comment in r.get_comments("mod",limit=100):
            
             #check that user is moderator
            if comment.author.name not in self.modlist[comment.subreddit.display_name]:
                continue
            
            #avoid duplicate work
            if comment.id in self.cache:
                continue
            
            self.cache.append(comment.id)
            
            acted_this_cycle=True
           
            print("processing comment "+comment.id+" by /u/"+comment.author.name)

            #enclose all mod actions in a big Try to protect against insufficient permissions
            try:
                if comment.body == "!ban":
                    parent_comment = r.get_info(thing_id=comment.parent_id)
                    comment.remove()
                    
                    parent_comment.remove()
                    comment.subreddit.add_ban(parent_comment.author)
                    self.log_entry(comment.subreddit, comment.author, parent_comment.author, "ban", comment.permalink)

                if comment.body == "!unban":
                    parent_comment = r.get_info(thing_id=comment.parent_id)
                    comment.remove()
                    
                    comment.subreddit.remove_ban(parent_comment.author)
                    self.log_entry(comment.subreddit, comment.author, parent_comment.author, "unban", comment.permalink)

                if "!flair" in comment.body:
                    parent = r.get_info(thing_id=comment.parent_id)
                    comment.remove()
                    acted_this_cycle=True
                    
                    #extract flair params
                    fclass = re.search("!flair( class=(\w+))? (.+)",comment.body).group(2)
                    ftext = re.search("!flair( class=(\w+))? (.+)",comment.body).group(3)
                    r.set_flair(comment.subreddit,parent.author.name,flair_text=ftext,flair_css_class=fclass)
                    self.log_entry(comment.subreddit, comment.author, parent.author, "flair: "+str(ftext)+"/"+str(fclass), comment.permalink)

                if comment.body == "!contrib":
                    parent = r.get_info(thing_id=comment.parent_id)
                    comment.remove()
                    
                    comment.subreddit.add_contributor(parent.author)
                    self.log_entry(comment.subreddit, comment.author, parent.author, "approve", comment.permalink)

                if comment.body == "!decontrib":
                    parent = r.get_info(thing_id=comment.parent_id)
                    comment.remove()
                    
                    comment.subreddit.remove_contributor(parent.author)
                    self.log_entry(comment.subreddit, comment.author, parent.author, "unapprove", comment.permalink)
                
                if comment.body =="!spam":
                    parent = r.get_info(thing_id=comment.parent_id)
                    comment.remove()
                    
                    parent.remove(spam=True)
                    r.submit("spam","overview for "+parent.author.name,url="http://reddit.com/user/"+parent.author.name)
                    self.log_entry(comment.subreddit, comment.author, parent.author, "spam", comment.permalink)
                    
            except praw.errors.ModeratorOrScopeRequired:
                r.send_message(comment.author, "Error", comment.permalink+"\n\n"+permissions_fail)

        if acted_this_cycle:
            r.edit_wiki_page("mod_button_bot_log","comment_cache",str(self.cache))

                    
    def update_moderators(self):

        print("Updating all moderators")

        for subreddit in r.get_my_moderation():
            self.update_moderators_in_subreddit(subreddit)

        r.edit_wiki_page("mod_button_bot_log","modlist_cache",str(self.modlist))

    def update_moderators_in_subreddit(self, subreddit):

        mods=[]
        for user in subreddit.get_moderators():
            if user.name != "AutoModerator" and user.name !=username:     #ignore automod and self
                mods.append(user.name)
        self.modlist[subreddit.display_name]=mods
        print("moderators loaded for /r/"+subreddit.display_name)
            
    def check_messages(self):

        for message in r.get_unread(limit=None):

            message.mark_as_read()
            #Just assume all messages are a mod invite, and fetch modlist if invite accepted
            try:
                r.accept_moderator_invite(message.subreddit.display_name)
                print("Accepted moderator invite for /r/"+message.subreddit.display_name)
                self.update_moderators_in_subreddit(message.subreddit)       
                #update cache
                r.edit_wiki_page("mod_button_bot_log","modlist_cache",str(self.modlist))  
                
                #send greeting
                msg="Hello, moderators of /r/"+message.subreddit.display_name+"!\n\n"
                msg=msg+"I am a bot designed to assist moderators using tablets, mobile devices, or any other reddit interface that does not support/permit extensions. Full details of my functionality may be found on [Github](http://github.com/captainmeta4/mod-button-bot).\n\n"
                msg=msg+"Please ensure that I have access, flair, posts, and wiki permissions for full functionality.\n\n"
                msg=msg+"I will log my actions at /r/"+message.subreddit.display_name+"/wiki/Mod_Button_Bot_Log. For the sake of accountability, if I am unable to log an action, I will send you a modmail instead.\n\n"
                msg=msg+"Feedback may be directed to my creator, /u/captainmeta4. Thanks for using me!"
                r.send_message(message.subreddit,"Hello!",msg)
                

                
            except:
                pass
            
            try:
                if message.author.name=="captainmeta4" and "reload mods" in message.body:
                    self.update_moderators()
            except:
                pass
            
    def log_entry(self, subreddit, modditor, redditor, action, url):
        #Post log entry to wiki
        entry = time.strftime("%c",time.gmtime())+" - /u/"+modditor.name+" "+action.upper()+" --> /u/"+redditor.name
        entry = "["+entry+"]("+url+"&context=3)"
        print(entry+" in /r/"+subreddit.display_name)
        try:
            wikipage = r.get_wiki_page(subreddit, "Mod_Button_Bot_Log").content_md
        except:
            wikipage = ''
        
        wikipage = "* "+entry + "\n\n"+ wikipage
        
        try:
            r.edit_wiki_page(subreddit, "Mod_Button_Bot_Log", wikipage,reason="action by "+modditor.name)
        except praw.errors.ModeratorOrScopeRequired:
            r.send_message(subreddit, "Moderator Action", "I just tried to log the following action, but I do not have wiki permissions:\n\n *"+entry)


modbot = Bot()

modbot.login_bot()

modbot.load_caches()

while 1:
    print("running cycle")
    
    #Once an hour, update mod list
    if time.localtime().tm_min==0 and time.localtime().tm_sec<29:
        modbot.update_moderators()
    
    modbot.check_messages()
    modbot.do_comments()
    print("sleeping..")

    #Run cycle on XX:XX:00 and XX:XX:30
    time.sleep(1)
    while time.localtime().tm_sec != 0 and time.localtime().tm_sec != 30:
        time.sleep(1)

