# Mod-Button-Bot
A bot that allows moderators to perform certain mod actions via comment commands.

Note - There is no PRAW method for determining if a moderator has a given moderator permission. Thus, this bot can't check for that, and so use of this bot will effectively give access, flair, and posts permissions to all moderators.

#Commands

Commands are issued by being a moderator and making a comment in your subreddit.

The bot refreshes its internal cache of moderators every hour at :00 , so if you add or remove mods, the bot will automatically adjust its behavior accordingly.

All functions automatically remove the moderator's command comment.

Command|Action
-------|--------
!flair|Sets user flair. Can be done as `!flair text goes here` or `!flair class=cssclass text goes here`. Both set the flair text to "text goes here"; the second example also sets the flair class to "cssclass"
!linkflair|Sets link flair. Syntax is same as `!flair`.
!spam|Removes the content as spam, and submits a /r/spam report.
!remove|Removes the content.
!approve|Approves the content
!report|Reports the content. Your name will be included in the report reason, along with any text following "!report" For example, "!report is this spam?" will produce a Moderator Report by the bot, with "yourname - is this spam?" as the report reason.
!rule|Removes the content, and leaves a comment directing the user to the sidebar. A number may be added, to indicate a specific rule, for example, `!rule 5` will result in the bot leaving a comment directing the user to look at Rule 5 in the sidebar.
!misleading|Flairs the submission as misleading, and leaves a distinguished comment explaining to read the linked article or review comments to get the full story.
!lockthread|Locks the comment thread via flair, and leaves a distinguished comment reminding users of the subreddit's commenting rules.

#Logging

To ensure that the bot is not abused to anonymously moderate, all actions are logged at a caching subreddit of your choice.
