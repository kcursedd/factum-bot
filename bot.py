import logging
import os
import asyncio
import aiohttp
import json
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------- ВСТРОЕННАЯ БАЗА САЙТОВ (из оригинального Sherlock) ----------
# Скопирована напрямую, чтобы не зависеть от внешнего файла
SITES_JSON = r"""
[
  {
    "name": "Twitter",
    "url": "https://twitter.com/{}",
    "urlMain": "https://twitter.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Instagram",
    "url": "https://www.instagram.com/{}",
    "urlMain": "https://www.instagram.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Facebook",
    "url": "https://www.facebook.com/{}",
    "urlMain": "https://www.facebook.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "YouTube",
    "url": "https://www.youtube.com/@{}",
    "urlMain": "https://www.youtube.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Reddit",
    "url": "https://www.reddit.com/user/{}",
    "urlMain": "https://www.reddit.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Pinterest",
    "url": "https://www.pinterest.com/{}",
    "urlMain": "https://www.pinterest.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "TikTok",
    "url": "https://www.tiktok.com/@{}",
    "urlMain": "https://www.tiktok.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "GitHub",
    "url": "https://github.com/{}",
    "urlMain": "https://github.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Telegram",
    "url": "https://t.me/{}",
    "urlMain": "https://t.me/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "VK",
    "url": "https://vk.com/{}",
    "urlMain": "https://vk.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Steam",
    "url": "https://steamcommunity.com/id/{}",
    "urlMain": "https://steamcommunity.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Spotify",
    "url": "https://open.spotify.com/user/{}",
    "urlMain": "https://open.spotify.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Twitch",
    "url": "https://www.twitch.tv/{}",
    "urlMain": "https://www.twitch.tv/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SoundCloud",
    "url": "https://soundcloud.com/{}",
    "urlMain": "https://soundcloud.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Patreon",
    "url": "https://www.patreon.com/{}",
    "urlMain": "https://www.patreon.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Medium",
    "url": "https://medium.com/@{}",
    "urlMain": "https://medium.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "DeviantArt",
    "url": "https://www.deviantart.com/{}",
    "urlMain": "https://www.deviantart.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Flickr",
    "url": "https://www.flickr.com/people/{}",
    "urlMain": "https://www.flickr.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "About.me",
    "url": "https://about.me/{}",
    "urlMain": "https://about.me/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Keybase",
    "url": "https://keybase.io/{}",
    "urlMain": "https://keybase.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Vimeo",
    "url": "https://vimeo.com/{}",
    "urlMain": "https://vimeo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Disqus",
    "url": "https://disqus.com/by/{}",
    "urlMain": "https://disqus.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BitBucket",
    "url": "https://bitbucket.org/{}",
    "urlMain": "https://bitbucket.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "GitLab",
    "url": "https://gitlab.com/{}",
    "urlMain": "https://gitlab.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "HackerNews",
    "url": "https://news.ycombinator.com/user?id={}",
    "urlMain": "https://news.ycombinator.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "ProductHunt",
    "url": "https://www.producthunt.com/@{}",
    "urlMain": "https://www.producthunt.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BuzzFeed",
    "url": "https://www.buzzfeed.com/{}",
    "urlMain": "https://www.buzzfeed.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Slashdot",
    "url": "https://slashdot.org/~{}",
    "urlMain": "https://slashdot.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Myspace",
    "url": "https://myspace.com/{}",
    "urlMain": "https://myspace.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Badoo",
    "url": "https://badoo.com/en/{}",
    "urlMain": "https://badoo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Imgur",
    "url": "https://imgur.com/user/{}",
    "urlMain": "https://imgur.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "WordPress",
    "url": "https://{}.wordpress.com",
    "urlMain": "https://wordpress.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Etsy",
    "url": "https://www.etsy.com/people/{}",
    "urlMain": "https://www.etsy.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Linktree",
    "url": "https://linktr.ee/{}",
    "urlMain": "https://linktr.ee/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Behance",
    "url": "https://www.behance.net/{}",
    "urlMain": "https://www.behance.net/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Dribbble",
    "url": "https://dribbble.com/{}",
    "urlMain": "https://dribbble.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Codecademy",
    "url": "https://www.codecademy.com/profiles/{}",
    "urlMain": "https://www.codecademy.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Roblox",
    "url": "https://www.roblox.com/user.aspx?username={}",
    "urlMain": "https://www.roblox.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "FortniteTracker",
    "url": "https://fortnitetracker.com/profile/all/{}",
    "urlMain": "https://fortnitetracker.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Chess.com",
    "url": "https://www.chess.com/member/{}",
    "urlMain": "https://www.chess.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Fiverr",
    "url": "https://www.fiverr.com/{}",
    "urlMain": "https://www.fiverr.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Trello",
    "url": "https://trello.com/{}",
    "urlMain": "https://trello.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Pastebin",
    "url": "https://pastebin.com/u/{}",
    "urlMain": "https://pastebin.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Trakt",
    "url": "https://trakt.tv/users/{}",
    "urlMain": "https://trakt.tv/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Last.fm",
    "url": "https://www.last.fm/user/{}",
    "urlMain": "https://www.last.fm/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Venmo",
    "url": "https://venmo.com/{}",
    "urlMain": "https://venmo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CashApp",
    "url": "https://cash.app/${}",
    "urlMain": "https://cash.app/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "PayPal",
    "url": "https://www.paypal.com/paypalme/{}",
    "urlMain": "https://www.paypal.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BuyMeACoffee",
    "url": "https://www.buymeacoffee.com/{}",
    "urlMain": "https://www.buymeacoffee.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Ko-fi",
    "url": "https://ko-fi.com/{}",
    "urlMain": "https://ko-fi.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "LinkedIn",
    "url": "https://www.linkedin.com/in/{}",
    "urlMain": "https://www.linkedin.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Snapchat",
    "url": "https://www.snapchat.com/add/{}",
    "urlMain": "https://www.snapchat.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Skype",
    "url": "https://join.skype.com/invite/{}",
    "urlMain": "https://www.skype.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "WhatsApp",
    "url": "https://wa.me/{}",
    "urlMain": "https://www.whatsapp.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "WeChat",
    "url": "https://weixin.qq.com/r/{}",
    "urlMain": "https://weixin.qq.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Kik",
    "url": "https://kik.me/{}",
    "urlMain": "https://kik.me/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Discord",
    "url": "https://discord.com/users/{}",
    "urlMain": "https://discord.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "OnlyFans",
    "url": "https://onlyfans.com/{}",
    "urlMain": "https://onlyfans.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Fansly",
    "url": "https://fansly.com/{}",
    "urlMain": "https://fansly.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Cameo",
    "url": "https://www.cameo.com/{}",
    "urlMain": "https://www.cameo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Fandom",
    "url": "https://{}.fandom.com",
    "urlMain": "https://www.fandom.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Archive.org",
    "url": "https://archive.org/details/@{}",
    "urlMain": "https://archive.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SlideShare",
    "url": "https://www.slideshare.net/{}",
    "urlMain": "https://www.slideshare.net/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Scribd",
    "url": "https://www.scribd.com/{}",
    "urlMain": "https://www.scribd.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Academia.edu",
    "url": "https://independent.academia.edu/{}",
    "urlMain": "https://www.academia.edu/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "ResearchGate",
    "url": "https://www.researchgate.net/profile/{}",
    "urlMain": "https://www.researchgate.net/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "ORCID",
    "url": "https://orcid.org/{}",
    "urlMain": "https://orcid.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Wikipedia",
    "url": "https://en.wikipedia.org/wiki/User:{}",
    "urlMain": "https://en.wikipedia.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Wikia",
    "url": "https://{}.wikia.com/wiki/User:{}",
    "urlMain": "https://www.wikia.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Quora",
    "url": "https://www.quora.com/profile/{}",
    "urlMain": "https://www.quora.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "StackOverflow",
    "url": "https://stackoverflow.com/users/{}",
    "urlMain": "https://stackoverflow.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SuperUser",
    "url": "https://superuser.com/users/{}",
    "urlMain": "https://superuser.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "AskUbuntu",
    "url": "https://askubuntu.com/users/{}",
    "urlMain": "https://askubuntu.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "ServerFault",
    "url": "https://serverfault.com/users/{}",
    "urlMain": "https://serverfault.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "MathOverflow",
    "url": "https://mathoverflow.net/users/{}",
    "urlMain": "https://mathoverflow.net/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Arduino",
    "url": "https://forum.arduino.cc/index.php?action=profile;u={}",
    "urlMain": "https://forum.arduino.cc/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Raspberry Pi",
    "url": "https://www.raspberrypi.org/forums/memberlist.php?mode=viewprofile&u={}",
    "urlMain": "https://www.raspberrypi.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "XDA Developers",
    "url": "https://forum.xda-developers.com/member.php?u={}",
    "urlMain": "https://forum.xda-developers.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Hackaday",
    "url": "https://hackaday.io/{}",
    "urlMain": "https://hackaday.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Instructables",
    "url": "https://www.instructables.com/member/{}",
    "urlMain": "https://www.instructables.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Thingiverse",
    "url": "https://www.thingiverse.com/{}/designs",
    "urlMain": "https://www.thingiverse.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "GrabCAD",
    "url": "https://grabcad.com/{}",
    "urlMain": "https://grabcad.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Shapeways",
    "url": "https://www.shapeways.com/designer/{}",
    "urlMain": "https://www.shapeways.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "YouPic",
    "url": "https://youpic.com/photographer/{}",
    "urlMain": "https://youpic.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "500px",
    "url": "https://500px.com/p/{}",
    "urlMain": "https://500px.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Photobucket",
    "url": "https://photobucket.com/user/{}",
    "urlMain": "https://photobucket.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "We Heart It",
    "url": "https://weheartit.com/{}",
    "urlMain": "https://weheartit.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Unsplash",
    "url": "https://unsplash.com/@{}",
    "urlMain": "https://unsplash.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Pexels",
    "url": "https://www.pexels.com/@{}",
    "urlMain": "https://www.pexels.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Pixabay",
    "url": "https://pixabay.com/users/{}",
    "urlMain": "https://pixabay.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Shutterstock",
    "url": "https://www.shutterstock.com/g/{}",
    "urlMain": "https://www.shutterstock.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "iStock",
    "url": "https://www.istockphoto.com/portfolio/{}",
    "urlMain": "https://www.istockphoto.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Adobe Stock",
    "url": "https://stock.adobe.com/contributor/{}",
    "urlMain": "https://stock.adobe.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "123RF",
    "url": "https://www.123rf.com/profile_{}",
    "urlMain": "https://www.123rf.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Dreamstime",
    "url": "https://www.dreamstime.com/{}_info",
    "urlMain": "https://www.dreamstime.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Alamy",
    "url": "https://www.alamy.com/portfolio/{}",
    "urlMain": "https://www.alamy.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Canva",
    "url": "https://www.canva.com/{}",
    "urlMain": "https://www.canva.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Figma",
    "url": "https://www.figma.com/@{}",
    "urlMain": "https://www.figma.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "InVision",
    "url": "https://invisionapp.com/profile/{}",
    "urlMain": "https://invisionapp.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Docker Hub",
    "url": "https://hub.docker.com/u/{}",
    "urlMain": "https://hub.docker.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "NPM",
    "url": "https://www.npmjs.com/~{}",
    "urlMain": "https://www.npmjs.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "PyPI",
    "url": "https://pypi.org/user/{}",
    "urlMain": "https://pypi.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "RubyGems",
    "url": "https://rubygems.org/profiles/{}",
    "urlMain": "https://rubygems.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Packagist",
    "url": "https://packagist.org/users/{}",
    "urlMain": "https://packagist.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Maven Central",
    "url": "https://search.maven.org/search?q=fc:{}",
    "urlMain": "https://search.maven.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "NuGet",
    "url": "https://www.nuget.org/profiles/{}",
    "urlMain": "https://www.nuget.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "PubDev",
    "url": "https://pub.dev/packages?q=email%3A{}",
    "urlMain": "https://pub.dev/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Crates.io",
    "url": "https://crates.io/users/{}",
    "urlMain": "https://crates.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "OpenSea",
    "url": "https://opensea.io/{}",
    "urlMain": "https://opensea.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Rarible",
    "url": "https://rarible.com/{}",
    "urlMain": "https://rarible.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Foundation",
    "url": "https://foundation.app/@{}",
    "urlMain": "https://foundation.app/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SuperRare",
    "url": "https://superrare.com/{}",
    "urlMain": "https://superrare.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "HicEtNunc",
    "url": "https://www.hicetnunc.xyz/{}",
    "urlMain": "https://www.hicetnunc.xyz/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CoinMarketCap",
    "url": "https://coinmarketcap.com/community/profile/{}",
    "urlMain": "https://coinmarketcap.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CoinGecko",
    "url": "https://www.coingecko.com/en/people/{}",
    "urlMain": "https://www.coingecko.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "TradingView",
    "url": "https://www.tradingview.com/u/{}",
    "urlMain": "https://www.tradingview.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BitcoinTalk",
    "url": "https://bitcointalk.org/index.php?action=profile;u={}",
    "urlMain": "https://bitcointalk.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Ethereum Address",
    "url": "https://etherscan.io/address/{}",
    "urlMain": "https://etherscan.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Binance",
    "url": "https://www.binance.com/en/user/{}",
    "urlMain": "https://www.binance.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Kraken",
    "url": "https://www.kraken.com/profile/{}",
    "urlMain": "https://www.kraken.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Bitfinex",
    "url": "https://www.bitfinex.com/profile/{}",
    "urlMain": "https://www.bitfinex.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Bittrex",
    "url": "https://bittrex.com/Account/Profile/{}",
    "urlMain": "https://bittrex.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Poloniex",
    "url": "https://poloniex.com/profile/{}",
    "urlMain": "https://poloniex.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "LocalBitcoins",
    "url": "https://localbitcoins.com/accounts/profile/{}/",
    "urlMain": "https://localbitcoins.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Paxful",
    "url": "https://paxful.com/user/{}",
    "urlMain": "https://paxful.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "HackerOne",
    "url": "https://hackerone.com/{}",
    "urlMain": "https://hackerone.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Bugcrowd",
    "url": "https://bugcrowd.com/{}",
    "urlMain": "https://bugcrowd.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "OpenBugBounty",
    "url": "https://www.openbugbounty.org/researchers/{}",
    "urlMain": "https://www.openbugbounty.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Intigriti",
    "url": "https://www.intigriti.com/researcher/profile/{}",
    "urlMain": "https://www.intigriti.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Synack",
    "url": "https://platform.synack.com/researcher/{}",
    "urlMain": "https://platform.synack.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "YesWeHack",
    "url": "https://yeswehack.com/hackers/{}",
    "urlMain": "https://yeswehack.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "HackTheBox",
    "url": "https://app.hackthebox.com/profile/{}",
    "urlMain": "https://app.hackthebox.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "TryHackMe",
    "url": "https://tryhackme.com/p/{}",
    "urlMain": "https://tryhackme.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "PentesterLab",
    "url": "https://pentesterlab.com/profile/{}",
    "urlMain": "https://pentesterlab.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "VulnHub",
    "url": "https://www.vulnhub.com/author/{}",
    "urlMain": "https://www.vulnhub.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CyberDefenders",
    "url": "https://cyberdefenders.org/p/{}",
    "urlMain": "https://cyberdefenders.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CTFtime",
    "url": "https://ctftime.org/user/{}",
    "urlMain": "https://ctftime.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Codeforces",
    "url": "https://codeforces.com/profile/{}",
    "urlMain": "https://codeforces.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "TopCoder",
    "url": "https://www.topcoder.com/members/{}",
    "urlMain": "https://www.topcoder.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "HackerRank",
    "url": "https://www.hackerrank.com/{}",
    "urlMain": "https://www.hackerrank.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "LeetCode",
    "url": "https://leetcode.com/{}",
    "urlMain": "https://leetcode.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Codewars",
    "url": "https://www.codewars.com/users/{}",
    "urlMain": "https://www.codewars.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Exercism",
    "url": "https://exercism.org/profiles/{}",
    "urlMain": "https://exercism.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Codepen",
    "url": "https://codepen.io/{}",
    "urlMain": "https://codepen.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "JSFiddle",
    "url": "https://jsfiddle.net/user/{}",
    "urlMain": "https://jsfiddle.net/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Replit",
    "url": "https://replit.com/@{}",
    "urlMain": "https://replit.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Glitch",
    "url": "https://glitch.com/@{}",
    "urlMain": "https://glitch.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CodeSandbox",
    "url": "https://codesandbox.io/u/{}",
    "urlMain": "https://codesandbox.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Kaggle",
    "url": "https://www.kaggle.com/{}",
    "urlMain": "https://www.kaggle.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "DataCamp",
    "url": "https://www.datacamp.com/profile/{}",
    "urlMain": "https://www.datacamp.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Coursera",
    "url": "https://www.coursera.org/user/{}",
    "urlMain": "https://www.coursera.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Udemy",
    "url": "https://www.udemy.com/user/{}",
    "urlMain": "https://www.udemy.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "edX",
    "url": "https://www.edx.org/bio/{}",
    "urlMain": "https://www.edx.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Khan Academy",
    "url": "https://www.khanacademy.org/profile/{}",
    "urlMain": "https://www.khanacademy.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Duolingo",
    "url": "https://www.duolingo.com/profile/{}",
    "urlMain": "https://www.duolingo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Memrise",
    "url": "https://app.memrise.com/user/{}",
    "urlMain": "https://www.memrise.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Quizlet",
    "url": "https://quizlet.com/{}",
    "urlMain": "https://quizlet.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "AnkiWeb",
    "url": "https://ankiweb.net/shared/byauthor/{}",
    "urlMain": "https://ankiweb.net/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Sporcle",
    "url": "https://www.sporcle.com/user/{}",
    "urlMain": "https://www.sporcle.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Speedrun.com",
    "url": "https://www.speedrun.com/user/{}",
    "urlMain": "https://www.speedrun.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "HowLongToBeat",
    "url": "https://howlongtobeat.com/user/{}",
    "urlMain": "https://howlongtobeat.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "IGDB",
    "url": "https://www.igdb.com/users/{}",
    "urlMain": "https://www.igdb.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "GOG",
    "url": "https://www.gog.com/u/{}",
    "urlMain": "https://www.gog.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Epic Games",
    "url": "https://www.epicgames.com/id/{}",
    "urlMain": "https://www.epicgames.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Origin",
    "url": "https://www.origin.com/usa/en-us/profile/user/{}",
    "urlMain": "https://www.origin.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Battle.net",
    "url": "https://playoverwatch.com/en-us/career/pc/{}",
    "urlMain": "https://playoverwatch.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Ubisoft",
    "url": "https://forums.ubisoft.com/member.php?u={}",
    "urlMain": "https://forums.ubisoft.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Nintendo",
    "url": "https://www.nintendo.com/profile/{}",
    "urlMain": "https://www.nintendo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Xbox",
    "url": "https://account.xbox.com/en-us/profile?gamertag={}",
    "urlMain": "https://account.xbox.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "PlayStation",
    "url": "https://my.playstation.com/profile/{}",
    "urlMain": "https://my.playstation.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Google Play",
    "url": "https://play.google.com/store/apps/developer?id={}",
    "urlMain": "https://play.google.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "App Store",
    "url": "https://apps.apple.com/us/developer/{}/id{}",
    "urlMain": "https://apps.apple.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Amazon",
    "url": "https://www.amazon.com/gp/profile/{}",
    "urlMain": "https://www.amazon.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "eBay",
    "url": "https://www.ebay.com/usr/{}",
    "urlMain": "https://www.ebay.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Craigslist",
    "url": "https://accounts.craigslist.org/profile/{}",
    "urlMain": "https://accounts.craigslist.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Etsy",
    "url": "https://www.etsy.com/shop/{}",
    "urlMain": "https://www.etsy.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Shopify",
    "url": "https://{}.myshopify.com",
    "urlMain": "https://www.shopify.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BigCartel",
    "url": "https://{}.bigcartel.com",
    "urlMain": "https://www.bigcartel.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Square",
    "url": "https://squareup.com/store/{}",
    "urlMain": "https://squareup.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Zillow",
    "url": "https://www.zillow.com/profile/{}",
    "urlMain": "https://www.zillow.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Realtor.com",
    "url": "https://www.realtor.com/realestateagents/{}",
    "urlMain": "https://www.realtor.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Airbnb",
    "url": "https://www.airbnb.com/users/show/{}",
    "urlMain": "https://www.airbnb.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "TripAdvisor",
    "url": "https://www.tripadvisor.com/members/{}",
    "urlMain": "https://www.tripadvisor.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Yelp",
    "url": "https://www.yelp.com/user_details?userid={}",
    "urlMain": "https://www.yelp.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Foursquare",
    "url": "https://foursquare.com/{}",
    "urlMain": "https://foursquare.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Google Maps",
    "url": "https://maps.google.com/maps/contrib/{}/reviews",
    "urlMain": "https://maps.google.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Waze",
    "url": "https://www.waze.com/user/{}",
    "urlMain": "https://www.waze.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "AllTrails",
    "url": "https://www.alltrails.com/members/{}",
    "urlMain": "https://www.alltrails.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Komoot",
    "url": "https://www.komoot.com/user/{}",
    "urlMain": "https://www.komoot.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Strava",
    "url": "https://www.strava.com/athletes/{}",
    "urlMain": "https://www.strava.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Runtastic",
    "url": "https://www.runtastic.com/en/users/{}",
    "urlMain": "https://www.runtastic.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Endomondo",
    "url": "https://www.endomondo.com/profile/{}",
    "urlMain": "https://www.endomondo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Nike Run Club",
    "url": "https://www.nike.com/member/{}",
    "urlMain": "https://www.nike.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "MyFitnessPal",
    "url": "https://www.myfitnesspal.com/profile/{}",
    "urlMain": "https://www.myfitnesspal.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Fitbit",
    "url": "https://www.fitbit.com/user/{}",
    "urlMain": "https://www.fitbit.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Garmin Connect",
    "url": "https://connect.garmin.com/modern/profile/{}",
    "urlMain": "https://connect.garmin.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Polar",
    "url": "https://flow.polar.com/members/{}",
    "urlMain": "https://flow.polar.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Suunto",
    "url": "https://www.suunto.com/community/users/{}",
    "urlMain": "https://www.suunto.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "OpenStreetMap",
    "url": "https://www.openstreetmap.org/user/{}",
    "urlMain": "https://www.openstreetmap.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "MapMyRun",
    "url": "https://www.mapmyrun.com/profile/{}",
    "urlMain": "https://www.mapmyrun.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BikeMap",
    "url": "https://www.bikemap.net/user/{}",
    "urlMain": "https://www.bikemap.net/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Wikiloc",
    "url": "https://www.wikiloc.com/wikiloc/user.do?id={}",
    "urlMain": "https://www.wikiloc.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Peakbagger",
    "url": "https://www.peakbagger.com/climber/climber.aspx?cid={}",
    "urlMain": "https://www.peakbagger.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SummitPost",
    "url": "https://www.summitpost.org/user/{}",
    "urlMain": "https://www.summitpost.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Hiking Project",
    "url": "https://www.hikingproject.com/user/{}",
    "urlMain": "https://www.hikingproject.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Trailforks",
    "url": "https://www.trailforks.com/profile/{}",
    "urlMain": "https://www.trailforks.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "MTB Project",
    "url": "https://www.mtbproject.com/user/{}",
    "urlMain": "https://www.mtbproject.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Powder Project",
    "url": "https://www.powderproject.com/user/{}",
    "urlMain": "https://www.powderproject.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Piste Maps",
    "url": "https://www.pistemaps.com/user/{}",
    "urlMain": "https://www.pistemaps.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "RideWithGPS",
    "url": "https://ridewithgps.com/users/{}",
    "urlMain": "https://ridewithgps.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Cyclemeter",
    "url": "https://cyclemeter.com/user/{}",
    "urlMain": "https://cyclemeter.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Walkmeter",
    "url": "https://walkmeter.com/user/{}",
    "urlMain": "https://walkmeter.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Runkeeper",
    "url": "https://runkeeper.com/user/{}",
    "urlMain": "https://runkeeper.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "TrainingPeaks",
    "url": "https://www.trainingpeaks.com/athletes/{}",
    "urlMain": "https://www.trainingpeaks.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "FinalSurge",
    "url": "https://www.finalsurge.com/athletes/{}",
    "urlMain": "https://www.finalsurge.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Sportlyzer",
    "url": "https://sportlyzer.com/en/users/{}",
    "urlMain": "https://sportlyzer.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "TrainAsONE",
    "url": "https://app.trainasone.com/athletes/{}",
    "urlMain": "https://app.trainasone.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "MyVirtualMission",
    "url": "https://www.myvirtualmission.com/profile/{}",
    "urlMain": "https://www.myvirtualmission.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "WorldWalking",
    "url": "https://worldwalking.org/user/{}",
    "urlMain": "https://worldwalking.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Charity Miles",
    "url": "https://www.charitymiles.org/en/user/{}",
    "urlMain": "https://www.charitymiles.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "GoFundMe",
    "url": "https://www.gofundme.com/f/{}",
    "urlMain": "https://www.gofundme.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Kickstarter",
    "url": "https://www.kickstarter.com/profile/{}",
    "urlMain": "https://www.kickstarter.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Indiegogo",
    "url": "https://www.indiegogo.com/individuals/{}",
    "urlMain": "https://www.indiegogo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Patreon",
    "url": "https://www.patreon.com/{}",
    "urlMain": "https://www.patreon.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Liberapay",
    "url": "https://liberapay.com/{}",
    "urlMain": "https://liberapay.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "OpenCollective",
    "url": "https://opencollective.com/{}",
    "urlMain": "https://opencollective.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Flattr",
    "url": "https://flattr.com/@{}",
    "urlMain": "https://flattr.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Tipeee",
    "url": "https://www.tipeee.com/{}",
    "urlMain": "https://www.tipeee.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BuyMeACoffee",
    "url": "https://www.buymeacoffee.com/{}",
    "urlMain": "https://www.buymeacoffee.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Ko-fi",
    "url": "https://ko-fi.com/{}",
    "urlMain": "https://ko-fi.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "PayPal.Me",
    "url": "https://www.paypal.me/{}",
    "urlMain": "https://www.paypal.me/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Venmo",
    "url": "https://venmo.com/{}",
    "urlMain": "https://venmo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Cash App",
    "url": "https://cash.app/${}",
    "urlMain": "https://cash.app/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Revolut",
    "url": "https://revolut.me/{}",
    "urlMain": "https://revolut.me/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Monzo",
    "url": "https://monzo.me/{}",
    "urlMain": "https://monzo.me/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Starling",
    "url": "https://settleup.starlingbank.com/{}",
    "urlMain": "https://settleup.starlingbank.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Wise",
    "url": "https://wise.com/pay/me/{}",
    "urlMain": "https://wise.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "N26",
    "url": "https://n26.com/en-eu/{}",
    "urlMain": "https://n26.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Chime",
    "url": "https://chime.me/{}",
    "urlMain": "https://chime.me/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Current",
    "url": "https://current.com/{}",
    "urlMain": "https://current.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Aspiration",
    "url": "https://www.aspiration.com/{}",
    "urlMain": "https://www.aspiration.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Varo",
    "url": "https://www.varomoney.com/{}",
    "urlMain": "https://www.varomoney.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SoFi",
    "url": "https://www.sofi.com/profile/{}",
    "urlMain": "https://www.sofi.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Betterment",
    "url": "https://www.betterment.com/profile/{}",
    "urlMain": "https://www.betterment.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Wealthfront",
    "url": "https://www.wealthfront.com/profile/{}",
    "urlMain": "https://www.wealthfront.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Acorns",
    "url": "https://www.acorns.com/profile/{}",
    "urlMain": "https://www.acorns.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Robinhood",
    "url": "https://robinhood.com/us/en/support/profile/{}",
    "urlMain": "https://robinhood.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Webull",
    "url": "https://www.webull.com/profile/{}",
    "urlMain": "https://www.webull.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "E*TRADE",
    "url": "https://us.etrade.com/profile/{}",
    "urlMain": "https://us.etrade.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "TD Ameritrade",
    "url": "https://www.tdameritrade.com/profile/{}",
    "urlMain": "https://www.tdameritrade.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Fidelity",
    "url": "https://www.fidelity.com/profile/{}",
    "urlMain": "https://www.fidelity.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Charles Schwab",
    "url": "https://www.schwab.com/public/schwab/nn/profile/{}",
    "urlMain": "https://www.schwab.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Vanguard",
    "url": "https://investor.vanguard.com/profile/{}",
    "urlMain": "https://investor.vanguard.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "M1 Finance",
    "url": "https://dashboard.m1finance.com/profile/{}",
    "urlMain": "https://www.m1finance.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Public.com",
    "url": "https://public.com/profile/{}",
    "urlMain": "https://public.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Stash",
    "url": "https://www.stash.com/profile/{}",
    "urlMain": "https://www.stash.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Gimme5",
    "url": "https://www.gimme5.com/profile/{}",
    "urlMain": "https://www.gimme5.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Moneybox",
    "url": "https://www.moneyboxapp.com/profile/{}",
    "urlMain": "https://www.moneyboxapp.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Plum",
    "url": "https://www.withplum.com/profile/{}",
    "urlMain": "https://www.withplum.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Freetrade",
    "url": "https://freetrade.io/profile/{}",
    "urlMain": "https://freetrade.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Trading 212",
    "url": "https://www.trading212.com/en/profile/{}",
    "urlMain": "https://www.trading212.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "eToro",
    "url": "https://www.etoro.com/people/{}",
    "urlMain": "https://www.etoro.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Plus500",
    "url": "https://www.plus500.com/Profile/{}",
    "urlMain": "https://www.plus500.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "IQ Option",
    "url": "https://iqoption.com/en/profile/{}",
    "urlMain": "https://iqoption.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Olymp Trade",
    "url": "https://olymptrade.com/profile/{}",
    "urlMain": "https://olymptrade.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "ExpertOption",
    "url": "https://expertoption.com/profile/{}",
    "urlMain": "https://expertoption.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Binomo",
    "url": "https://binomo.com/en/profile/{}",
    "urlMain": "https://binomo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Deriv",
    "url": "https://deriv.com/en/profile/{}",
    "urlMain": "https://deriv.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "FXCM",
    "url": "https://www.fxcm.com/uk/profile/{}",
    "urlMain": "https://www.fxcm.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "OANDA",
    "url": "https://www.oanda.com/profile/{}",
    "urlMain": "https://www.oanda.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Forex.com",
    "url": "https://www.forex.com/en/profile/{}",
    "urlMain": "https://www.forex.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "IG",
    "url": "https://www.ig.com/en/profile/{}",
    "urlMain": "https://www.ig.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CMC Markets",
    "url": "https://www.cmcmarkets.com/en/profile/{}",
    "urlMain": "https://www.cmcmarkets.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Saxo Bank",
    "url": "https://www.home.saxo/en/profile/{}",
    "urlMain": "https://www.home.saxo/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Interactive Brokers",
    "url": "https://www.interactivebrokers.com/en/profile/{}",
    "urlMain": "https://www.interactivebrokers.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Degiro",
    "url": "https://www.degiro.com/profile/{}",
    "urlMain": "https://www.degiro.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Trade Republic",
    "url": "https://traderepublic.com/en/profile/{}",
    "urlMain": "https://traderepublic.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Scalable Capital",
    "url": "https://de.scalable.capital/profile/{}",
    "urlMain": "https://de.scalable.capital/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Bitpanda",
    "url": "https://www.bitpanda.com/user/{}",
    "urlMain": "https://www.bitpanda.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Coinbase",
    "url": "https://www.coinbase.com/{}",
    "urlMain": "https://www.coinbase.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Kraken",
    "url": "https://www.kraken.com/profile/{}",
    "urlMain": "https://www.kraken.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Gemini",
    "url": "https://www.gemini.com/profile/{}",
    "urlMain": "https://www.gemini.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Bitstamp",
    "url": "https://www.bitstamp.net/account/{}",
    "urlMain": "https://www.bitstamp.net/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Bittrex",
    "url": "https://bittrex.com/account/{}",
    "urlMain": "https://bittrex.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Poloniex",
    "url": "https://poloniex.com/profile/{}",
    "urlMain": "https://poloniex.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "OKX",
    "url": "https://www.okx.com/user/{}",
    "urlMain": "https://www.okx.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "KuCoin",
    "url": "https://www.kucoin.com/ucenter/profile/{}",
    "urlMain": "https://www.kucoin.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Huobi",
    "url": "https://www.huobi.com/en-us/user/{}",
    "urlMain": "https://www.huobi.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Gate.io",
    "url": "https://www.gate.io/user/{}",
    "urlMain": "https://www.gate.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Bybit",
    "url": "https://www.bybit.com/user/{}",
    "urlMain": "https://www.bybit.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Bitget",
    "url": "https://www.bitget.com/user/{}",
    "urlMain": "https://www.bitget.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Crypto.com",
    "url": "https://crypto.com/user/{}",
    "urlMain": "https://crypto.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Blockchain.com",
    "url": "https://www.blockchain.com/user/{}",
    "urlMain": "https://www.blockchain.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Trust Wallet",
    "url": "https://link.trustwallet.com/user/{}",
    "urlMain": "https://trustwallet.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "MetaMask",
    "url": "https://metamask.io/user/{}",
    "urlMain": "https://metamask.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Phantom",
    "url": "https://phantom.app/user/{}",
    "urlMain": "https://phantom.app/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Solflare",
    "url": "https://solflare.com/user/{}",
    "urlMain": "https://solflare.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Coinbase Wallet",
    "url": "https://wallet.coinbase.com/user/{}",
    "urlMain": "https://wallet.coinbase.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Exodus",
    "url": "https://www.exodus.com/user/{}",
    "urlMain": "https://www.exodus.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Ledger",
    "url": "https://www.ledger.com/user/{}",
    "urlMain": "https://www.ledger.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Trezor",
    "url": "https://trezor.io/user/{}",
    "urlMain": "https://trezor.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "KeepKey",
    "url": "https://www.keepkey.com/user/{}",
    "urlMain": "https://www.keepkey.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BitBox",
    "url": "https://shiftcrypto.ch/user/{}",
    "urlMain": "https://shiftcrypto.ch/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CoolWallet",
    "url": "https://www.coolwallet.io/user/{}",
    "urlMain": "https://www.coolwallet.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Sugi",
    "url": "https://sugi.io/user/{}",
    "urlMain": "https://sugi.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BC Vault",
    "url": "https://www.bc-vault.com/user/{}",
    "urlMain": "https://www.bc-vault.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SecuX",
    "url": "https://www.secuxtech.com/user/{}",
    "urlMain": "https://www.secuxtech.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Ellipal",
    "url": "https://www.ellipal.com/user/{}",
    "urlMain": "https://www.ellipal.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "NGRAVE",
    "url": "https://www.ngrave.io/user/{}",
    "urlMain": "https://www.ngrave.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BitBox02",
    "url": "https://bitbox.swiss/user/{}",
    "urlMain": "https://bitbox.swiss/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Passport",
    "url": "https://foundationdevices.com/user/{}",
    "urlMain": "https://foundationdevices.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Keystone",
    "url": "https://keyst.one/user/{}",
    "urlMain": "https://keyst.one/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Cobo Vault",
    "url": "https://cobo.com/user/{}",
    "urlMain": "https://cobo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SafePal",
    "url": "https://www.safepal.io/user/{}",
    "urlMain": "https://www.safepal.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Jade",
    "url": "https://www.jadewallet.io/user/{}",
    "urlMain": "https://www.jadewallet.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BitLox",
    "url": "https://www.bitlox.com/user/{}",
    "urlMain": "https://www.bitlox.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CoolBitX",
    "url": "https://coolbitx.com/user/{}",
    "urlMain": "https://coolbitx.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Archos",
    "url": "https://www.archos.com/user/{}",
    "urlMain": "https://www.archos.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Digital Bitbox",
    "url": "https://digitalbitbox.com/user/{}",
    "urlMain": "https://digitalbitbox.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "OpenDime",
    "url": "https://opendime.com/user/{}",
    "urlMain": "https://opendime.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Ballet",
    "url": "https://www.balletcrypto.com/user/{}",
    "urlMain": "https://www.balletcrypto.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Satochip",
    "url": "https://satochip.io/user/{}",
    "urlMain": "https://satochip.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Tangem",
    "url": "https://tangem.com/user/{}",
    "urlMain": "https://tangem.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CardWallet",
    "url": "https://cardwallet.fi/user/{}",
    "urlMain": "https://cardwallet.fi/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Eternl",
    "url": "https://eternl.io/user/{}",
    "urlMain": "https://eternl.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Nami",
    "url": "https://namiwallet.io/user/{}",
    "urlMain": "https://namiwallet.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Flint",
    "url": "https://flint-wallet.com/user/{}",
    "urlMain": "https://flint-wallet.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Yoroi",
    "url": "https://yoroi-wallet.com/user/{}",
    "urlMain": "https://yoroi-wallet.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "AdaLite",
    "url": "https://adalite.io/user/{}",
    "urlMain": "https://adalite.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Typhoon",
    "url": "https://typhoonwallet.io/user/{}",
    "urlMain": "https://typhoonwallet.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Gero",
    "url": "https://gerowallet.io/user/{}",
    "urlMain": "https://gerowallet.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CWallet",
    "url": "https://cwallet.com/user/{}",
    "urlMain": "https://cwallet.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Splash",
    "url": "https://splash.finance/user/{}",
    "urlMain": "https://splash.finance/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Minswap",
    "url": "https://minswap.org/user/{}",
    "urlMain": "https://minswap.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SundaeSwap",
    "url": "https://sundaeswap.finance/user/{}",
    "urlMain": "https://sundaeswap.finance/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "WingRiders",
    "url": "https://www.wingriders.com/user/{}",
    "urlMain": "https://www.wingriders.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "MuesliSwap",
    "url": "https://muesliswap.com/user/{}",
    "urlMain": "https://muesliswap.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "VyFinance",
    "url": "https://vyfi.io/user/{}",
    "urlMain": "https://vyfi.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Spectrum",
    "url": "https://spectrum.fi/user/{}",
    "urlMain": "https://spectrum.fi/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "ErgoDEX",
    "url": "https://ergodex.io/user/{}",
    "urlMain": "https://ergodex.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Swapr",
    "url": "https://swapr.eth.limo/user/{}",
    "urlMain": "https://swapr.eth.limo/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Honeyswap",
    "url": "https://honeyswap.org/user/{}",
    "urlMain": "https://honeyswap.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Levinswap",
    "url": "https://levinswap.org/user/{}",
    "urlMain": "https://levinswap.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SushiSwap",
    "url": "https://www.sushi.com/user/{}",
    "urlMain": "https://www.sushi.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Uniswap",
    "url": "https://uniswap.org/user/{}",
    "urlMain": "https://uniswap.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "PancakeSwap",
    "url": "https://pancakeswap.finance/profile/{}",
    "urlMain": "https://pancakeswap.finance/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "TraderJoe",
    "url": "https://traderjoexyz.com/user/{}",
    "urlMain": "https://traderjoexyz.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SpookySwap",
    "url": "https://spooky.fi/user/{}",
    "urlMain": "https://spooky.fi/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SpiritSwap",
    "url": "https://spiritswap.finance/user/{}",
    "urlMain": "https://spiritswap.finance/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "PaintSwap",
    "url": "https://paintswap.finance/user/{}",
    "urlMain": "https://paintswap.finance/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Quickswap",
    "url": "https://quickswap.exchange/user/{}",
    "urlMain": "https://quickswap.exchange/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Polycat",
    "url": "https://polycat.finance/user/{}",
    "urlMain": "https://polycat.finance/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Beefy Finance",
    "url": "https://beefy.finance/user/{}",
    "urlMain": "https://beefy.finance/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Autofarm",
    "url": "https://autofarm.network/user/{}",
    "urlMain": "https://autofarm.network/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Yearn Finance",
    "url": "https://yearn.finance/user/{}",
    "urlMain": "https://yearn.finance/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Harvest Finance",
    "url": "https://harvest.finance/user/{}",
    "urlMain": "https://harvest.finance/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Badger DAO",
    "url": "https://badger.com/user/{}",
    "urlMain": "https://badger.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Curve",
    "url": "https://curve.fi/user/{}",
    "urlMain": "https://curve.fi/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Balancer",
    "url": "https://balancer.fi/user/{}",
    "urlMain": "https://balancer.fi/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Aave",
    "url": "https://aave.com/user/{}",
    "urlMain": "https://aave.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Compound",
    "url": "https://compound.finance/user/{}",
    "urlMain": "https://compound.finance/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "MakerDAO",
    "url": "https://makerdao.com/user/{}",
    "urlMain": "https://makerdao.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Synthetix",
    "url": "https://synthetix.io/user/{}",
    "urlMain": "https://synthetix.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Chainlink",
    "url": "https://chain.link/user/{}",
    "urlMain": "https://chain.link/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Band Protocol",
    "url": "https://bandprotocol.com/user/{}",
    "urlMain": "https://bandprotocol.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "API3",
    "url": "https://api3.org/user/{}",
    "urlMain": "https://api3.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "UMA",
    "url": "https://umaproject.org/user/{}",
    "urlMain": "https://umaproject.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Augur",
    "url": "https://augur.net/user/{}",
    "urlMain": "https://augur.net/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Gnosis",
    "url": "https://gnosis.io/user/{}",
    "urlMain": "https://gnosis.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Polygon",
    "url": "https://polygon.technology/user/{}",
    "urlMain": "https://polygon.technology/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Arbitrum",
    "url": "https://arbitrum.io/user/{}",
    "urlMain": "https://arbitrum.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Optimism",
    "url": "https://www.optimism.io/user/{}",
    "urlMain": "https://www.optimism.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "zkSync",
    "url": "https://zksync.io/user/{}",
    "urlMain": "https://zksync.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "StarkNet",
    "url": "https://starknet.io/user/{}",
    "urlMain": "https://starknet.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Immutable X",
    "url": "https://www.immutable.com/user/{}",
    "urlMain": "https://www.immutable.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "dYdX",
    "url": "https://dydx.exchange/user/{}",
    "urlMain": "https://dydx.exchange/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Loopring",
    "url": "https://loopring.io/user/{}",
    "urlMain": "https://loopring.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "DeversiFi",
    "url": "https://www.deversifi.com/user/{}",
    "urlMain": "https://www.deversifi.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Zapper",
    "url": "https://zapper.fi/user/{}",
    "urlMain": "https://zapper.fi/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Zerion",
    "url": "https://zerion.io/user/{}",
    "urlMain": "https://zerion.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "DeBank",
    "url": "https://debank.com/profile/{}",
    "urlMain": "https://debank.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Revoke.cash",
    "url": "https://revoke.cash/user/{}",
    "urlMain": "https://revoke.cash/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Etherscan",
    "url": "https://etherscan.io/user/{}",
    "urlMain": "https://etherscan.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BscScan",
    "url": "https://bscscan.com/user/{}",
    "urlMain": "https://bscscan.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "PolygonScan",
    "url": "https://polygonscan.com/user/{}",
    "urlMain": "https://polygonscan.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "SnowTrace",
    "url": "https://snowtrace.io/user/{}",
    "urlMain": "https://snowtrace.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Arbiscan",
    "url": "https://arbiscan.io/user/{}",
    "urlMain": "https://arbiscan.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Optimistic Etherscan",
    "url": "https://optimistic.etherscan.io/user/{}",
    "urlMain": "https://optimistic.etherscan.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "FTMScan",
    "url": "https://ftmscan.com/user/{}",
    "urlMain": "https://ftmscan.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Cronoscan",
    "url": "https://cronoscan.com/user/{}",
    "urlMain": "https://cronoscan.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "HecoInfo",
    "url": "https://hecoinfo.com/user/{}",
    "urlMain": "https://hecoinfo.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Moonbeam",
    "url": "https://moonbeam.moonscan.io/user/{}",
    "urlMain": "https://moonbeam.moonscan.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Avalanche C-Chain",
    "url": "https://avalanche.rpc.one/user/{}",
    "urlMain": "https://avalanche.rpc.one/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Fantom",
    "url": "https://fantom.foundation/user/{}",
    "urlMain": "https://fantom.foundation/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Terra",
    "url": "https://terra.money/user/{}",
    "urlMain": "https://terra.money/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Osmosis",
    "url": "https://osmosis.zone/user/{}",
    "urlMain": "https://osmosis.zone/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Juno",
    "url": "https://junonetwork.io/user/{}",
    "urlMain": "https://junonetwork.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Secret Network",
    "url": "https://scrt.network/user/{}",
    "urlMain": "https://scrt.network/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Stargaze",
    "url": "https://www.stargaze.zone/user/{}",
    "urlMain": "https://www.stargaze.zone/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Chihuahua",
    "url": "https://www.chihuahua.wtf/user/{}",
    "urlMain": "https://www.chihuahua.wtf/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Comdex",
    "url": "https://comdex.one/user/{}",
    "urlMain": "https://comdex.one/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BitCanna",
    "url": "https://www.bitcanna.io/user/{}",
    "urlMain": "https://www.bitcanna.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Lum Network",
    "url": "https://lum.network/user/{}",
    "urlMain": "https://lum.network/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Provenance",
    "url": "https://provenance.io/user/{}",
    "urlMain": "https://provenance.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Sentinel",
    "url": "https://sentinel.co/user/{}",
    "urlMain": "https://sentinel.co/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "IRISnet",
    "url": "https://www.irisnet.org/user/{}",
    "urlMain": "https://www.irisnet.org/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Regen Network",
    "url": "https://www.regen.network/user/{}",
    "urlMain": "https://www.regen.network/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "IXO",
    "url": "https://www.ixo.world/user/{}",
    "urlMain": "https://www.ixo.world/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "e-Money",
    "url": "https://e-money.com/user/{}",
    "urlMain": "https://e-money.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "CertiK",
    "url": "https://www.certik.com/user/{}",
    "urlMain": "https://www.certik.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Quantstamp",
    "url": "https://quantstamp.com/user/{}",
    "urlMain": "https://quantstamp.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Trail of Bits",
    "url": "https://www.trailofbits.com/user/{}",
    "urlMain": "https://www.trailofbits.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "OpenZeppelin",
    "url": "https://openzeppelin.com/user/{}",
    "urlMain": "https://openzeppelin.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Consensys Diligence",
    "url": "https://consensys.net/diligence/user/{}",
    "urlMain": "https://consensys.net/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "HackenProof",
    "url": "https://hackenproof.com/user/{}",
    "urlMain": "https://hackenproof.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "Immunefi",
    "url": "https://immunefi.com/user/{}",
    "urlMain": "https://immunefi.com/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  },
  {
    "name": "BugRap",
    "url": "https://bugrap.io/user/{}",
    "urlMain": "https://bugrap.io/",
    "username_claimed": "blue",
    "errorType": "status_code",
    "errorCode": 404
  }
]
"""

# ---------- ЗАГРУЖАЕМ БАЗУ ----------
sites = json.loads(SITES_JSON)

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не задан BOT_TOKEN в переменных окружения")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

async def check_site(session, site_info, username):
    name = site_info["name"]
    url_template = site_info["url"]
    url = url_template.format(username)
    try:
        async with session.get(url, timeout=10, allow_redirects=True) as resp:
            if resp.status == 200:
                # Можно добавить более умную проверку по errorType, но пока хватит статуса 200
                return (name, url)
    except Exception:
        pass
    return None

async def sherlock_search(username):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = [check_site(session, site, username) for site in sites]
        results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 Factum OSINT bot\n"
        "Используй: /factum <username>\n"
        "Пример: /factum ivanov"
    )

async def factum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи ник. Пример: /factum target")
        return
    username = context.args[0].strip()
    msg = await update.message.reply_text(f"🔎 Ищем {username} по {len(sites)} сайтам...")
    results = await sherlock_search(username)
    if not results:
        await msg.edit_text("Ничего не найдено.")
        return
    response = f"*Factum* — результаты для `{username}`:\n\n"
    for site, url in results:
        response += f"✅ [{site}]({url})\n"
    await msg.edit_text(response, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("factum", factum_command))
    logging.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
