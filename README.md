# Telegram Reaction Bot

an automated bot uses Telethon Library for doing reactions to a Telegram channel post.

## Edit Config

To edit the config.py file 

```
CHANNELS_LIST = ['4XZhZqXpo6Q1NDg1']
CHANNEL_IDS = ['-1002112202931']
```

The CHANNELS_LIST Contain the Channel Private Link

* if link is like https://t.me/+4XZhZqXpo6Q1NDg1
* Then You Have To Use 4XZhZqXpo6Q1NDg1 Which is Your Channel Link

## To Get CHANNEL ID 

* Visit @chat_id_echo_bot on Telegran
* Then Forward an Message From Your Channel To Bot 
* It will Provide You the Chat ID 

```
EMOJIS = ['👍', '❤️', '🔥', '🥰', '👏', '🎉', '🤩', '⚡️', '💯']
```

* You Can Also Change The Emojis 

## Create a session file manually.

Create a file Session1.ini ( the file name can be anything ) in the directory /sessions :

```
[Telethon]
api_id=YOUR_API_ID
api_hash=YOUR_API_HASH
phone_number=YOUR_PHONE_NUMBER
```

## Where do I get `api_id` and `api_hash`?

 [🔗 Click me.](https://my.telegram.org/auth)

## Deployment

To deploy this You need Python3 Installed on System
Follow The Commend To Install Bot

```Python
  pip install -r requirements.txt
  python reactionbot.py
```

Phone Number should be with Country Code 

## Contact

- 📫  Contact Email - [Click Me](mailto:neoscript77@proton.me)

## Authors

- [@kanewi11](https://github.com/kanewi11/telegram-reaction-bot)

I have Made a few changes on it..
