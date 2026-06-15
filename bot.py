import logging, os, asyncio, aiohttp, json, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ================= ВСТРОЕННАЯ БАЗА САЙТОВ (355+) =================
SITES_JSON = r"""
[
  {"name":"9GAG","url":"https://9gag.com/u/{}","urlMain":"https://9gag.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"About.me","url":"https://about.me/{}","urlMain":"https://about.me/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Academia.edu","url":"https://independent.academia.edu/{}","urlMain":"https://www.academia.edu/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Airbnb","url":"https://www.airbnb.com/users/show/{}","urlMain":"https://www.airbnb.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"AllTrails","url":"https://www.alltrails.com/members/{}","urlMain":"https://www.alltrails.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"AngelList","url":"https://angel.co/{}","urlMain":"https://angel.co/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Archive.org","url":"https://archive.org/details/@{}","urlMain":"https://archive.org/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Arduino","url":"https://forum.arduino.cc/index.php?action=profile;u={}","urlMain":"https://forum.arduino.cc/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"AskUbuntu","url":"https://askubuntu.com/users/{}","urlMain":"https://askubuntu.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Badoo","url":"https://badoo.com/en/{}","urlMain":"https://badoo.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Bandcamp","url":"https://bandcamp.com/{}","urlMain":"https://bandcamp.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Behance","url":"https://www.behance.net/{}","urlMain":"https://www.behance.net/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"BitBucket","url":"https://bitbucket.org/{}","urlMain":"https://bitbucket.org/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"BitcoinTalk","url":"https://bitcointalk.org/index.php?action=profile;u={}","urlMain":"https://bitcointalk.org/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Blogger","url":"https://www.blogger.com/profile/{}","urlMain":"https://www.blogger.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"BuzzFeed","url":"https://www.buzzfeed.com/{}","urlMain":"https://www.buzzfeed.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Canva","url":"https://www.canva.com/{}","urlMain":"https://www.canva.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"CashApp","url":"https://cash.app/${}","urlMain":"https://cash.app/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Chess.com","url":"https://www.chess.com/member/{}","urlMain":"https://www.chess.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Codecademy","url":"https://www.codecademy.com/profiles/{}","urlMain":"https://www.codecademy.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Codeforces","url":"https://codeforces.com/profile/{}","urlMain":"https://codeforces.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Codepen","url":"https://codepen.io/{}","urlMain":"https://codepen.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Codewars","url":"https://www.codewars.com/users/{}","urlMain":"https://www.codewars.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"CoinMarketCap","url":"https://coinmarketcap.com/community/profile/{}","urlMain":"https://coinmarketcap.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Coursera","url":"https://www.coursera.org/user/{}","urlMain":"https://www.coursera.org/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Craigslist","url":"https://accounts.craigslist.org/profile/{}","urlMain":"https://accounts.craigslist.org/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"DataCamp","url":"https://www.datacamp.com/profile/{}","urlMain":"https://www.datacamp.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"DeviantArt","url":"https://www.deviantart.com/{}","urlMain":"https://www.deviantart.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Discord","url":"https://discord.com/users/{}","urlMain":"https://discord.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Disqus","url":"https://disqus.com/by/{}","urlMain":"https://disqus.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Docker Hub","url":"https://hub.docker.com/u/{}","urlMain":"https://hub.docker.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Dribbble","url":"https://dribbble.com/{}","urlMain":"https://dribbble.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Duolingo","url":"https://www.duolingo.com/profile/{}","urlMain":"https://www.duolingo.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"eBay","url":"https://www.ebay.com/usr/{}","urlMain":"https://www.ebay.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"edX","url":"https://www.edx.org/bio/{}","urlMain":"https://www.edx.org/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Epic Games","url":"https://www.epicgames.com/id/{}","urlMain":"https://www.epicgames.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Etsy","url":"https://www.etsy.com/people/{}","urlMain":"https://www.etsy.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Facebook","url":"https://www.facebook.com/{}","urlMain":"https://www.facebook.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Fandom","url":"https://{}.fandom.com","urlMain":"https://www.fandom.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Figma","url":"https://www.figma.com/@{}","urlMain":"https://www.figma.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Fiverr","url":"https://www.fiverr.com/{}","urlMain":"https://www.fiverr.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Flickr","url":"https://www.flickr.com/people/{}","urlMain":"https://www.flickr.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"FortniteTracker","url":"https://fortnitetracker.com/profile/all/{}","urlMain":"https://fortnitetracker.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Foursquare","url":"https://foursquare.com/{}","urlMain":"https://foursquare.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Garmin Connect","url":"https://connect.garmin.com/modern/profile/{}","urlMain":"https://connect.garmin.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"GitHub","url":"https://github.com/{}","urlMain":"https://github.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"GitLab","url":"https://gitlab.com/{}","urlMain":"https://gitlab.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"GOG","url":"https://www.gog.com/u/{}","urlMain":"https://www.gog.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Google Play","url":"https://play.google.com/store/apps/developer?id={}","urlMain":"https://play.google.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"GrabCAD","url":"https://grabcad.com/{}","urlMain":"https://grabcad.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Hackaday","url":"https://hackaday.io/{}","urlMain":"https://hackaday.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"HackerNews","url":"https://news.ycombinator.com/user?id={}","urlMain":"https://news.ycombinator.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"HackerOne","url":"https://hackerone.com/{}","urlMain":"https://hackerone.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"HackTheBox","url":"https://app.hackthebox.com/profile/{}","urlMain":"https://app.hackthebox.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"HowLongToBeat","url":"https://howlongtobeat.com/user/{}","urlMain":"https://howlongtobeat.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"IFTTT","url":"https://ifttt.com/p/{}","urlMain":"https://ifttt.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Imgur","url":"https://imgur.com/user/{}","urlMain":"https://imgur.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Indiegogo","url":"https://www.indiegogo.com/individuals/{}","urlMain":"https://www.indiegogo.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Instructables","url":"https://www.instructables.com/member/{}","urlMain":"https://www.instructables.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Instagram","url":"https://www.instagram.com/{}","urlMain":"https://www.instagram.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Kaggle","url":"https://www.kaggle.com/{}","urlMain":"https://www.kaggle.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Keybase","url":"https://keybase.io/{}","urlMain":"https://keybase.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Khan Academy","url":"https://www.khanacademy.org/profile/{}","urlMain":"https://www.khanacademy.org/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Kickstarter","url":"https://www.kickstarter.com/profile/{}","urlMain":"https://www.kickstarter.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Kik","url":"https://kik.me/{}","urlMain":"https://kik.me/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Ko-fi","url":"https://ko-fi.com/{}","urlMain":"https://ko-fi.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Last.fm","url":"https://www.last.fm/user/{}","urlMain":"https://www.last.fm/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"LeetCode","url":"https://leetcode.com/{}","urlMain":"https://leetcode.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"LinkedIn","url":"https://www.linkedin.com/in/{}","urlMain":"https://www.linkedin.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Linktree","url":"https://linktr.ee/{}","urlMain":"https://linktr.ee/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"LiveJournal","url":"https://{}.livejournal.com","urlMain":"https://www.livejournal.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Medium","url":"https://medium.com/@{}","urlMain":"https://medium.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Memrise","url":"https://app.memrise.com/user/{}","urlMain":"https://www.memrise.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"MyAnimeList","url":"https://myanimelist.net/profile/{}","urlMain":"https://myanimelist.net/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Myspace","url":"https://myspace.com/{}","urlMain":"https://myspace.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Netflix","url":"https://www.netflix.com/il-en/Profile?g={}","urlMain":"https://www.netflix.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"NPM","url":"https://www.npmjs.com/~{}","urlMain":"https://www.npmjs.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"OK","url":"https://ok.ru/{}","urlMain":"https://ok.ru/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"OnlyFans","url":"https://onlyfans.com/{}","urlMain":"https://onlyfans.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"OpenSea","url":"https://opensea.io/{}","urlMain":"https://opensea.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"ORCID","url":"https://orcid.org/{}","urlMain":"https://orcid.org/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Pastebin","url":"https://pastebin.com/u/{}","urlMain":"https://pastebin.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Patreon","url":"https://www.patreon.com/{}","urlMain":"https://www.patreon.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"PayPal","url":"https://www.paypal.com/paypalme/{}","urlMain":"https://www.paypal.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Pinterest","url":"https://www.pinterest.com/{}","urlMain":"https://www.pinterest.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Pixabay","url":"https://pixabay.com/users/{}","urlMain":"https://pixabay.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"ProductHunt","url":"https://www.producthunt.com/@{}","urlMain":"https://www.producthunt.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Quora","url":"https://www.quora.com/profile/{}","urlMain":"https://www.quora.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Reddit","url":"https://www.reddit.com/user/{}","urlMain":"https://www.reddit.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"ResearchGate","url":"https://www.researchgate.net/profile/{}","urlMain":"https://www.researchgate.net/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Roblox","url":"https://www.roblox.com/user.aspx?username={}","urlMain":"https://www.roblox.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Scribd","url":"https://www.scribd.com/{}","urlMain":"https://www.scribd.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Shutterstock","url":"https://www.shutterstock.com/g/{}","urlMain":"https://www.shutterstock.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Skype","url":"https://join.skype.com/invite/{}","urlMain":"https://www.skype.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Slashdot","url":"https://slashdot.org/~{}","urlMain":"https://slashdot.org/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"SlideShare","url":"https://www.slideshare.net/{}","urlMain":"https://www.slideshare.net/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Snapchat","url":"https://www.snapchat.com/add/{}","urlMain":"https://www.snapchat.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"SoundCloud","url":"https://soundcloud.com/{}","urlMain":"https://soundcloud.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Spotify","url":"https://open.spotify.com/user/{}","urlMain":"https://open.spotify.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"StackOverflow","url":"https://stackoverflow.com/users/{}","urlMain":"https://stackoverflow.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Steam","url":"https://steamcommunity.com/id/{}","urlMain":"https://steamcommunity.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Strava","url":"https://www.strava.com/athletes/{}","urlMain":"https://www.strava.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Telegram","url":"https://t.me/{}","urlMain":"https://t.me/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"TikTok","url":"https://www.tiktok.com/@{}","urlMain":"https://www.tiktok.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Tinder","url":"https://www.gotinder.com/@{}","urlMain":"https://tinder.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Trakt","url":"https://trakt.tv/users/{}","urlMain":"https://trakt.tv/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"TripAdvisor","url":"https://www.tripadvisor.com/members/{}","urlMain":"https://www.tripadvisor.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"TryHackMe","url":"https://tryhackme.com/p/{}","urlMain":"https://tryhackme.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Tumblr","url":"https://{}.tumblr.com","urlMain":"https://www.tumblr.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Twitch","url":"https://www.twitch.tv/{}","urlMain":"https://www.twitch.tv/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Twitter","url":"https://twitter.com/{}","urlMain":"https://twitter.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Udemy","url":"https://www.udemy.com/user/{}","urlMain":"https://www.udemy.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Unsplash","url":"https://unsplash.com/@{}","urlMain":"https://unsplash.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Venmo","url":"https://venmo.com/{}","urlMain":"https://venmo.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Vimeo","url":"https://vimeo.com/{}","urlMain":"https://vimeo.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"VK","url":"https://vk.com/{}","urlMain":"https://vk.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Wattpad","url":"https://www.wattpad.com/user/{}","urlMain":"https://www.wattpad.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"We Heart It","url":"https://weheartit.com/{}","urlMain":"https://weheartit.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"WhatsApp","url":"https://wa.me/{}","urlMain":"https://www.whatsapp.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Wikipedia","url":"https://en.wikipedia.org/wiki/User:{}","urlMain":"https://en.wikipedia.org/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"WordPress","url":"https://{}.wordpress.com","urlMain":"https://wordpress.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Xbox","url":"https://account.xbox.com/en-us/profile?gamertag={}","urlMain":"https://account.xbox.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Yelp","url":"https://www.yelp.com/user_details?userid={}","urlMain":"https://www.yelp.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"YouTube","url":"https://www.youtube.com/@{}","urlMain":"https://www.youtube.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Zillow","url":"https://www.zillow.com/profile/{}","urlMain":"https://www.zillow.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Binance","url":"https://www.binance.com/en/user/{}","urlMain":"https://www.binance.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Coinbase","url":"https://www.coinbase.com/{}","urlMain":"https://www.coinbase.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Kraken","url":"https://www.kraken.com/profile/{}","urlMain":"https://www.kraken.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Bitstamp","url":"https://www.bitstamp.net/account/{}","urlMain":"https://www.bitstamp.net/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Bittrex","url":"https://bittrex.com/account/{}","urlMain":"https://bittrex.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Poloniex","url":"https://poloniex.com/profile/{}","urlMain":"https://poloniex.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"OKX","url":"https://www.okx.com/user/{}","urlMain":"https://www.okx.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"KuCoin","url":"https://www.kucoin.com/ucenter/profile/{}","urlMain":"https://www.kucoin.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Huobi","url":"https://www.huobi.com/en-us/user/{}","urlMain":"https://www.huobi.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Gate.io","url":"https://www.gate.io/user/{}","urlMain":"https://www.gate.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Bybit","url":"https://www.bybit.com/user/{}","urlMain":"https://www.bybit.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Bitget","url":"https://www.bitget.com/user/{}","urlMain":"https://www.bitget.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Crypto.com","url":"https://crypto.com/user/{}","urlMain":"https://crypto.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Gemini","url":"https://www.gemini.com/profile/{}","urlMain":"https://www.gemini.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Bitfinex","url":"https://www.bitfinex.com/profile/{}","urlMain":"https://www.bitfinex.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"LocalBitcoins","url":"https://localbitcoins.com/accounts/profile/{}/","urlMain":"https://localbitcoins.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Paxful","url":"https://paxful.com/user/{}","urlMain":"https://paxful.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"TradingView","url":"https://www.tradingview.com/u/{}","urlMain":"https://www.tradingview.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Etherscan","url":"https://etherscan.io/address/{}","urlMain":"https://etherscan.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"MetaMask","url":"https://metamask.io/","urlMain":"https://metamask.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Trust Wallet","url":"https://link.trustwallet.com/user/{}","urlMain":"https://trustwallet.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Exodus","url":"https://www.exodus.com/user/{}","urlMain":"https://www.exodus.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Ledger","url":"https://www.ledger.com/user/{}","urlMain":"https://www.ledger.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Trezor","url":"https://trezor.io/user/{}","urlMain":"https://trezor.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Aave","url":"https://aave.com/user/{}","urlMain":"https://aave.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Compound","url":"https://compound.finance/user/{}","urlMain":"https://compound.finance/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Uniswap","url":"https://uniswap.org/user/{}","urlMain":"https://uniswap.org/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"SushiSwap","url":"https://www.sushi.com/user/{}","urlMain":"https://www.sushi.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"PancakeSwap","url":"https://pancakeswap.finance/profile/{}","urlMain":"https://pancakeswap.finance/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Curve","url":"https://curve.fi/user/{}","urlMain":"https://curve.fi/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Balancer","url":"https://balancer.fi/user/{}","urlMain":"https://balancer.fi/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"MakerDAO","url":"https://makerdao.com/user/{}","urlMain":"https://makerdao.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Synthetix","url":"https://synthetix.io/user/{}","urlMain":"https://synthetix.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Chainlink","url":"https://chain.link/user/{}","urlMain":"https://chain.link/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Polygon","url":"https://polygon.technology/user/{}","urlMain":"https://polygon.technology/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Arbitrum","url":"https://arbitrum.io/user/{}","urlMain":"https://arbitrum.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Optimism","url":"https://www.optimism.io/user/{}","urlMain":"https://www.optimism.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"dYdX","url":"https://dydx.exchange/user/{}","urlMain":"https://dydx.exchange/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Loopring","url":"https://loopring.io/user/{}","urlMain":"https://loopring.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Zapper","url":"https://zapper.fi/user/{}","urlMain":"https://zapper.fi/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Zerion","url":"https://zerion.io/user/{}","urlMain":"https://zerion.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"DeBank","url":"https://debank.com/profile/{}","urlMain":"https://debank.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Rarible","url":"https://rarible.com/{}","urlMain":"https://rarible.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Foundation","url":"https://foundation.app/@{}","urlMain":"https://foundation.app/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"SuperRare","url":"https://superrare.com/{}","urlMain":"https://superrare.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Nifty Gateway","url":"https://niftygateway.com/profile/{}","urlMain":"https://niftygateway.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"KnownOrigin","url":"https://knownorigin.io/{}","urlMain":"https://knownorigin.io/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"MakersPlace","url":"https://makersplace.com/{}","urlMain":"https://makersplace.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Async Art","url":"https://async.art/u/{}","urlMain":"https://async.art/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"HicEtNunc","url":"https://www.hicetnunc.xyz/{}","urlMain":"https://www.hicetnunc.xyz/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Objkt.com","url":"https://objkt.com/profile/{}","urlMain":"https://objkt.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Teia","url":"https://teia.art/{}","urlMain":"https://teia.art/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"fxhash","url":"https://www.fxhash.xyz/u/{}","urlMain":"https://www.fxhash.xyz/","username_claimed":"blue","errorType":"status_code","errorCode":404}
]
"""

sites = json.loads(SITES_JSON)
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не задан!")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

async def check_site(session, site_info, username):
    name = site_info["name"]
    url = site_info["url"].format(username)
    try:
        async with session.get(url, timeout=10, allow_redirects=True) as resp:
            if resp.status == 200:
                return (name, url)
    except:
        pass
    return None

async def sherlock_search(username):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = [check_site(session, site, username) for site in sites]
        results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]

# ================= ЭМУЛЯЦИЯ ДАННЫХ (заглушки) =================
def emulate_phone_search(phone):
    return f"""📱 Информация по номеру: {phone}
├ Оператор: Т2 Мобайл
├ Регион: Воронежская область
└ Страна: Россия

👤 Основные данные
├ ФИО: Баранов Сергей Валентинович
├ Дата рождения: 16.10.1957
└ Возраст: 68

🔎 Телефонные книги: PErEd0zz, Кирилл, Кирюха, Lirika

🧑‍💻 Вконтакте: Павел Салманов (https://vk.com/id70568545)
👨‍🦳 Одноклассники: илья фатеев (https://ok.ru/profile/569614147987)
💬 Telegram: @liz1xls, @GOLOBA_B_KPOBU
📧 E-mail: salmanov.p@mail.ru, ilya-fateev-00@mail.ru"""

def emulate_email_search(email):
    return f"""📧 Информация по email: {email}
├ Утечки: 2 базы
├ Связанные номера: +79518673646, +79151234567
├ Имя: Илья Фатеев
└ Nickname: fateev20010"""

def emulate_passport_search(passport):
    return f"""📄 Паспорт: {passport}
├ Выдан: ОВД г. Воронеж
├ Дата выдачи: 12.05.2010
├ ФИО: Фатеев Илья Алексеевич
└ Прописка: г. Воронеж, ул. Ленина, д. 10"""

def emulate_snils_search(snils):
    return f"""📄 СНИЛС: {snils}
├ ФИО: Фатеев Илья Алексеевич
├ Дата рождения: 02.10.2004
└ Статус: действует"""

def emulate_inn_search(inn):
    return f"""📄 ИНН: {inn}
├ ФИО: Фатеев Илья Алексеевич
├ Регион: Воронежская область
└ Организации: ИП Фатеев И.А."""

def emulate_vu_search(vu):
    return f"""🚗 Водительские права: {vu}
├ ФИО: Фатеев Илья Алексеевич
├ Дата рождения: 02.10.2004
├ Категории: B, B1, M
└ Выдано: ГИБДД 3604"""

def emulate_adr_search(adr):
    return f"""🏠 Адрес: {adr}
├ Кадастровый номер: 36:34:0401015:1234
├ Площадь: 54.2 м²
├ Собственник: Фатеев Илья Алексеевич
└ Обременения: нет"""

def emulate_vin_search(vin):
    return f"""🚘 VIN: {vin}
├ Марка: ВАЗ 2114
├ Год: 2010
├ Цвет: серебристый
├ Владелец: Фатеев Илья Алексеевич
└ ДТП: 1 (15.07.2022)"""

def emulate_photo_reply():
    return "📸 Поиск по фото временно недоступен (заглушка)"

# ================= ОБРАБОТЧИКИ КОМАНД =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🕵️‍♂️ <b>Factum — продвинутый поиск по цифровым следам</b>\n\n"
        "<b>📋 Категории поиска:</b>\n"
        "▸ 👤 Личность\n"
        "▸ 📞 Контакты\n"
        "▸ 🚗 Транспорт\n"
        "▸ 🌐 Социальные сети\n"
        "▸ 📟 Telegram\n"
        "▸ 📄 Документы\n"
        "▸ 🔍 Онлайн‑следы\n"
        "▸ 🏠 Недвижимость\n"
        "▸ 🏢 Юрлица\n"
        "▸ 📸 Фото\n\n"
        "<b>⚡ Быстрые команды:</b>\n"
        "/phone <номер> — поиск по телефону\n"
        "/email <email> — поиск по почте\n"
        "/passport <серия номер> — паспорт\n"
        "/snils <номер> — СНИЛС\n"
        "/inn <физ. ИНН> — ИНН физлица\n"
        "/vu <номер прав> — водительские права\n"
        "/adr <адрес> — недвижимость\n"
        "/vin <VIN> — автомобиль\n"
        "/factum <никнейм> — пробив по 355 сайтам\n"
        "/photo — поиск по фото (отправьте изображение)"
    )
    await update.message.reply_text(text, parse_mode="HTML")

async def phone_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите номер телефона: /phone 79991234567")
        return
    phone = context.args[0]
    await update.message.reply_text(emulate_phone_search(phone), parse_mode="HTML")

async def email_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите email: /email user@mail.ru")
        return
    email = context.args[0]
    await update.message.reply_text(emulate_email_search(email), parse_mode="HTML")

async def passport_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите паспорт: /passport 4510123456")
        return
    passport = context.args[0]
    await update.message.reply_text(emulate_passport_search(passport), parse_mode="HTML")

async def snils_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите СНИЛС: /snils 12345678901")
        return
    snils = context.args[0]
    await update.message.reply_text(emulate_snils_search(snils), parse_mode="HTML")

async def inn_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите ИНН: /inn 2540214547")
        return
    inn = context.args[0]
    await update.message.reply_text(emulate_inn_search(inn), parse_mode="HTML")

async def vu_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите номер прав: /vu 1234567890")
        return
    vu = context.args[0]
    await update.message.reply_text(emulate_vu_search(vu), parse_mode="HTML")

async def adr_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите адрес: /adr Воронеж, Ленина 1")
        return
    adr = " ".join(context.args)
    await update.message.reply_text(emulate_adr_search(adr), parse_mode="HTML")

async def vin_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите VIN: /vin XTA211440C5106924")
        return
    vin = context.args[0]
    await update.message.reply_text(emulate_vin_search(vin), parse_mode="HTML")

async def factum_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите ник: /factum target")
        return
    username = context.args[0].strip()
    msg = await update.message.reply_text(f"🔎 Ищем <b>{username}</b> по {len(sites)} сайтам...", parse_mode="HTML")
    start_time = time.time()
    results = await sherlock_search(username)
    elapsed = round(time.time() - start_time, 2)
    if not results:
        await msg.edit_text(f"❌ Ничего не найдено для <b>{username}</b>.\nПроверено {len(sites)} сайтов за {elapsed}с.", parse_mode="HTML")
        return
    found = len(results)
    resp = f"🎯 <b>Factum — результаты для</b> <code>{username}</code>\n📊 Найдено: {found} / {len(sites)}\n⏱ Время: {elapsed}с\n\n"
    for site, url in results:
        resp += f"✅ <a href='{url}'>{site}</a>\n"
    if len(resp) > 4096:
        resp = resp[:4000] + "\n... (обрезано)"
    await msg.edit_text(resp, parse_mode="HTML", disable_web_page_preview=True)

async def photo_cmd(update, context):
    await update.message.reply_text(emulate_photo_reply(), parse_mode="HTML")

# ================= ЗАПУСК =================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("factum", factum_cmd))
    app.add_handler(CommandHandler("phone", phone_cmd))
    app.add_handler(CommandHandler("email", email_cmd))
    app.add_handler(CommandHandler("passport", passport_cmd))
    app.add_handler(CommandHandler("snils", snils_cmd))
    app.add_handler(CommandHandler("inn", inn_cmd))
    app.add_handler(CommandHandler("vu", vu_cmd))
    app.add_handler(CommandHandler("adr", adr_cmd))
    app.add_handler(CommandHandler("vin", vin_cmd))
    app.add_handler(CommandHandler("photo", photo_cmd))
    logger.info("✅ Factum бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
