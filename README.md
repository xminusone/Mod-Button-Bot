# Mod-Button-Bot
A bot that replicates some of the functionality of Toolbox's mod button for moderators on mobile.

To add this to your subreddit, add /u/Mod_Button_Bot as a moderator with at least access, flair, posts, and wiki permissions.

Note - There is no PRAW method for determining if a moderator has a given moderator permission. Thus, this bot can't check for that, and so use of this bot will effectively give access, flair, and posts permissions to all moderators.

#Commands

Commands are issued by being a moderator and making a comment in your subreddit.

All functions automatically remove the moderator's command comment.

##!ban

Bans the user and removes the comment.

##!unban

Unbans the user.

##!flair

Sets user flair. Can be done as `!flair text goes here` or `!flair class=cssclass text goes here`.

Both set the flair text to "text goes here"; the second example also sets the flair class to "cssclass"

##!contrib

Adds the user as an approved contributor to the subreddit.

##!decontrib

Removes the user from the approved contributor list.

##!spam

Removes the content as spam, and submits a /r/spam report.

#Logging

To ensure that /u/Mod\_Button\_bot is not abused to anonymously moderate, all actions are logged at /r/subredditname/wiki/Mod\_Button\_Bot\_Log.
