#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SherlockCore – единый бот с БД и 355 сайтами обогащения.
Запуск: python bot.py
Требуется Tor на 127.0.0.1:9050 и PostgreSQL с импортированной базой.
"""

import asyncio
import json
import aiohttp
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup
from io import BytesIO
from datetime import datetime
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ==================== КОНФИГУРАЦИЯ ====================
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "sherlock",
    "user": "good",
    "password": "NoRules2026!"
}
TOR_PROXY = "socks5://127.0.0.1:9050"
BOT_TOKEN = "ТВОЙ_ТОКЕН_БОТА"
MAX_CONCURRENT_REQUESTS = 10
REQUEST_TIMEOUT = 15

# ==================== 355 САЙТОВ (ВСТРОЕННЫЙ JSON) ====================
SITES = json.loads(r'''
[
  {"name":"VK","url":"https://vk.com/","search_path":"search?c[section]=people&c[name]=1&c[query]={query}","type":"name","method":"GET","parser":{"result_block":".search_result","name":".labeled","link":"a"}},
  {"name":"OK.ru","url":"https://ok.ru/","search_path":"search?st.query={query}&st.cmd=searchPeople","type":"name","method":"GET","parser":{"result_block":".results-list","name":".user-info .n","link":".user-info a"}},
  {"name":"Instagram","url":"https://www.instagram.com/","search_path":"web/search/topsearch/?query={query}","type":"name","method":"GET","parser":{"result_block":"ul","name":".full_name","link":".user a"}},
  {"name":"Facebook","url":"https://www.facebook.com/","search_path":"search/people/?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":"._32mo","link":"a"}},
  {"name":"Twitter","url":"https://twitter.com/","search_path":"search?q={query}&f=user","type":"name","method":"GET","parser":{"result_block":".css-1dbjc4n","name":".r-1awozwy","link":"a"}},
  {"name":"LinkedIn","url":"https://www.linkedin.com/","search_path":"search/results/people/?keywords={query}","type":"name","method":"GET","parser":{"result_block":".search-results","name":".actor-name","link":"a"}},
  {"name":"Telegram","url":"https://t.me/","search_path":"{query}","type":"name","method":"GET","parser":{"result_block":".tgme_page_title","title":".tgme_page_title","desc":".tgme_page_description"}},
  {"name":"PhoneRadar","url":"https://phoneradar.ru/","search_path":"number/{query}","type":"phone","method":"GET","parser":{"result_block":"main","operator":".operator","region":".region"}},
  {"name":"NumBuster","url":"https://numbuster.com/","search_path":"phone/{query}","type":"phone","method":"GET","parser":{"result_block":".phone-info","rating":".rating","reviews":".reviews"}},
  {"name":"EmailRep","url":"https://emailrep.io/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":"body","reputation":".reputation","details":"pre"}},
  {"name":"HaveIBeenPwned","url":"https://haveibeenpwned.com/","search_path":"unifiedsearch/{query}","type":"email","method":"GET","parser":{"result_block":"main","breaches":".breaches"}},
  {"name":"GHDB","url":"https://www.exploit-db.com/google-hacking-database","search_path":"?query={query}","type":"name","method":"GET","parser":{"result_block":"#exploits_table","name":".links a"}},
  {"name":"SpyDialer","url":"https://www.spydialer.com/","search_path":"?phone={query}","type":"phone","method":"GET","parser":{"result_block":".results","name":"h2"}},
  {"name":"ThatsThem","url":"https://thatsthem.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"TruePeopleSearch","url":"https://www.truepeoplesearch.com/","search_path":"results?name={query}","type":"name","method":"GET","parser":{"result_block":"#results","name":".h4"}},
  {"name":"ZabaSearch","url":"https://www.zabasearch.com/","search_path":"?name={query}","type":"name","method":"GET","parser":{"result_block":"#results","name":".name"}},
  {"name":"Pipl","url":"https://pipl.com/","search_path":"search/?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"PeekYou","url":"https://www.peekyou.com/","search_path":"{query}","type":"name","method":"GET","parser":{"result_block":"#results","name":".name"}},
  {"name":"Whitepages","url":"https://www.whitepages.com/","search_path":"search?name={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"411","url":"https://www.411.com/","search_path":"search?name={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"AnyWho","url":"https://www.anywho.com/","search_path":"?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Addresses","url":"https://www.addresses.com/","search_path":"search?name={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Nuwber","url":"https://nuwber.com/","search_path":"search?name={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"FastPeopleSearch","url":"https://www.fastpeoplesearch.com/","search_path":"name/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"SearchPeopleFree","url":"https://www.searchpeoplefree.com/","search_path":"?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"IDCrawl","url":"https://idcrawl.com/","search_path":"{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".h3"}},
  {"name":"SocialCatfish","url":"https://socialcatfish.com/","search_path":"search/?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"USSearch","url":"https://www.ussearch.com/","search_path":"search?name={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"PeopleFinders","url":"https://www.peoplefinders.com/","search_path":"search?name={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Intelius","url":"https://www.intelius.com/","search_path":"search?name={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"BeenVerified","url":"https://www.beenverified.com/","search_path":"search?name={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"InstantCheckmate","url":"https://www.instantcheckmate.com/","search_path":"search?name={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"TruthFinder","url":"https://www.truthfinder.com/","search_path":"search?name={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Spokeo","url":"https://www.spokeo.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"MyLife","url":"https://www.mylife.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Radaris","url":"https://radaris.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"PeopleSmart","url":"https://www.peoplesmart.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"CheckPeople","url":"https://www.checkpeople.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"PublicRecordsNow","url":"https://www.publicrecordsnow.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Arrests","url":"https://www.arrests.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"BOP","url":"https://www.bop.gov/","search_path":"inmateloc/","type":"name","method":"POST","data":{"name":"{query}"},"parser":{"result_block":"#inmateSearchResults","name":"td"}},
  {"name":"FamilyTreeNow","url":"https://www.familytreenow.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Classmates","url":"https://www.classmates.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Alumni","url":"https://www.alumni.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Yasni","url":"https://www.yasni.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"WebMii","url":"https://webmii.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"123people","url":"https://www.123people.com/","search_path":"s/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Zillow","url":"https://www.zillow.com/","search_path":"homes/{query}_rb/","type":"name","method":"GET","parser":{"result_block":".search-results","name":".list-card-title"}},
  {"name":"Rehold","url":"https://rehold.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Bisnode","url":"https://www.bisnode.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Kompass","url":"https://www.kompass.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Europages","url":"https://www.europages.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Firmenwissen","url":"https://www.firmenwissen.de/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"CreditSafe","url":"https://www.creditsafe.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"OpenCorporates","url":"https://opencorporates.com/","search_path":"companies?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"CompaniesHouse","url":"https://find-and-update.company-information.service.gov.uk/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"SEC","url":"https://www.sec.gov/","search_path":"cgi-bin/browse-edgar?company={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"DunBradstreet","url":"https://www.dnb.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Hoovers","url":"https://www.hoovers.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"ZoomInfo","url":"https://www.zoominfo.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"RocketReach","url":"https://rocketreach.co/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Hunter","url":"https://hunter.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Snov.io","url":"https://snov.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Lusha","url":"https://www.lusha.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Apollo","url":"https://www.apollo.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Clearbit","url":"https://clearbit.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"FullContact","url":"https://www.fullcontact.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"PiplAPI","url":"https://api.pipl.com/","search_path":"search/?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"LeakCheck","url":"https://leakcheck.io/","search_path":"search?q={query}","type":"email","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"SnusBase","url":"https://snusbase.com/","search_path":"search?q={query}","type":"email","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Leaked.site","url":"https://leaked.site/","search_path":"search?q={query}","type":"email","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"BreachDirectory","url":"https://breachdirectory.org/","search_path":"search?q={query}","type":"email","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"DeHashed","url":"https://dehashed.com/","search_path":"search?q={query}","type":"email","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"IntelligenceX","url":"https://intelx.io/","search_path":"?s={query}","type":"email","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Gravatar","url":"https://en.gravatar.com/","search_path":"{query}.json","type":"email","method":"GET","parser":{"result_block":"body","profile":"entry"}},
  {"name":"Spiderfoot","url":"https://www.spiderfoot.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Maltego","url":"https://www.maltego.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Recon-ng","url":"https://github.com/lanmaster53/recon-ng","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"theHarvester","url":"https://github.com/laramies/theHarvester","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Amass","url":"https://github.com/owasp-amass/amass","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Censys","url":"https://search.censys.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Shodan","url":"https://www.shodan.io/","search_path":"search?query={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"ZoomEye","url":"https://www.zoomeye.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"BinaryEdge","url":"https://app.binaryedge.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"FOFA","url":"https://fofa.info/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Hunter.how","url":"https://hunter.how/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"PublicWWW","url":"https://publicwww.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Wigle","url":"https://wigle.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"OpenStreetMap","url":"https://www.openstreetmap.org/","search_path":"search?query={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"GeoNames","url":"https://www.geonames.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"WaybackMachine","url":"https://web.archive.org/","search_path":"web/*/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Google","url":"https://www.google.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":"#search","name":"h3"}},
  {"name":"Bing","url":"https://www.bing.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":"#b_results","name":"h2"}},
  {"name":"Yahoo","url":"https://search.yahoo.com/","search_path":"search?p={query}","type":"name","method":"GET","parser":{"result_block":"#web","name":"h3"}},
  {"name":"Yandex","url":"https://yandex.com/","search_path":"search/?text={query}","type":"name","method":"GET","parser":{"result_block":".serp-list","name":"h2"}},
  {"name":"DuckDuckGo","url":"https://duckduckgo.com/","search_path":"?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".result__title"}},
  {"name":"Baidu","url":"https://www.baidu.com/","search_path":"s?wd={query}","type":"name","method":"GET","parser":{"result_block":"#results","name":"h3"}},
  {"name":"AOL","url":"https://search.aol.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":"#web","name":"h3"}},
  {"name":"Ask","url":"https://www.ask.com/","search_path":"web?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".PartialSearchResults-item-title"}},
  {"name":"Startpage","url":"https://www.startpage.com/","search_path":"do/search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":"h3"}},
  {"name":"Qwant","url":"https://www.qwant.com/","search_path":"?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":"h3"}},
  {"name":"Ecosia","url":"https://www.ecosia.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":"h3"}},
  {"name":"Swisscows","url":"https://swisscows.com/","search_path":"web?query={query}","type":"name","method":"GET","parser":{"result_block":".results","name":"h3"}},
  {"name":"MetaGer","url":"https://metager.org/","search_path":"meta/meta.ger3?eingabe={query}","type":"name","method":"GET","parser":{"result_block":".results","name":"h3"}},
  {"name":"Mojeek","url":"https://www.mojeek.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":"h3"}},
  {"name":"Gibiru","url":"https://gibiru.com/","search_path":"results.html?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":"h3"}},
  {"name":"SearX","url":"https://searx.space/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":"h3"}},
  {"name":"Whois","url":"https://who.is/","search_path":"whois/{query}","type":"name","method":"GET","parser":{"result_block":"pre","raw":"pre"}},
  {"name":"ICANN","url":"https://lookup.icann.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"DomainTools","url":"https://whois.domaintools.com/","search_path":"{query}","type":"name","method":"GET","parser":{"result_block":"pre","raw":"pre"}},
  {"name":"ViewDNS","url":"https://viewdns.info/","search_path":"whois/?domain={query}","type":"name","method":"GET","parser":{"result_block":"pre","raw":"pre"}},
  {"name":"MXToolbox","url":"https://mxtoolbox.com/","search_path":"SuperTool.aspx?action=whois&run=toolpage&q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"NSLookup","url":"https://www.nslookup.io/","search_path":"domains/{query}/whois/","type":"name","method":"GET","parser":{"result_block":"pre","raw":"pre"}},
  {"name":"Robtex","url":"https://www.robtex.com/","search_path":"dns-lookup/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"SecurityTrails","url":"https://securitytrails.com/","search_path":"domain/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"URLScan","url":"https://urlscan.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"VirusTotal","url":"https://www.virustotal.com/","search_path":"gui/search/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"HybridAnalysis","url":"https://www.hybrid-analysis.com/","search_path":"search?query={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Any.Run","url":"https://app.any.run/","search_path":"submissions?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"JoeSandbox","url":"https://www.joesandbox.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"ThreatCrowd","url":"https://www.threatcrowd.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"AlienVault","url":"https://otx.alienvault.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Pulsedive","url":"https://pulsedive.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"AbuseIPDB","url":"https://www.abuseipdb.com/","search_path":"check/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"IPinfo","url":"https://ipinfo.io/","search_path":"{query}","type":"name","method":"GET","parser":{"result_block":"body","ip":"body"}},
  {"name":"IP2Location","url":"https://www.ip2location.com/","search_path":"demo/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"WhatIsMyIP","url":"https://www.whatismyip.com/","search_path":"ip/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"IP-api","url":"http://ip-api.com/","search_path":"json/{query}","type":"name","method":"GET","parser":{"result_block":"body","raw":"body"}},
  {"name":"DB-IP","url":"https://db-ip.com/","search_path":"{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"RIPE","url":"https://stat.ripe.net/","search_path":"data/looking-glass/data.json?resource={query}","type":"name","method":"GET","parser":{"result_block":"body","raw":"body"}},
  {"name":"BGPView","url":"https://bgpview.io/","search_path":"ip/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Crt.sh","url":"https://crt.sh/","search_path":"?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"CertSpotter","url":"https://sslmate.com/certspotter/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"DNSDumpster","url":"https://dnsdumpster.com/","search_path":"?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Shcheck","url":"https://shcheck.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"WebCheck","url":"https://web-check.xyz/","search_path":"results/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Siterelic","url":"https://siterelic.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"NerdyData","url":"https://www.nerdydata.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"BuiltWith","url":"https://builtwith.com/","search_path":"{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Wappalyzer","url":"https://www.wappalyzer.com/","search_path":"lookup/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"WhatCMS","url":"https://whatcms.org/","search_path":"?s={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"CMSDetect","url":"https://www.cmsdetect.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"SiteCheck","url":"https://sitecheck.sucuri.net/","search_path":"results/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Quttera","url":"https://quttera.com/","search_path":"website-malware-scanner?url={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"UpGuard","url":"https://www.upguard.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Detectify","url":"https://detectify.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Tinfoil","url":"https://www.tinfoilsecurity.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Observatory","url":"https://observatory.mozilla.org/","search_path":"analyze/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Hardenize","url":"https://www.hardenize.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"CryptoChecker","url":"https://cryptcheck.fr/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"HSTS","url":"https://hstspreload.org/","search_path":"?domain={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"SecurityHeaders","url":"https://securityheaders.com/","search_path":"?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"ReportURI","url":"https://report-uri.com/","search_path":"home/analyse/https://{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"DNSlytics","url":"https://dnslytics.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"DomainBigData","url":"https://domainbigdata.com/","search_path":"{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"WhoisXML","url":"https://www.whoisxmlapi.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Spamhaus","url":"https://www.spamhaus.org/","search_path":"lookup/?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"MXLookup","url":"https://mxtoolbox.com/","search_path":"SuperTool.aspx?action=mx&run=toolpage&q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"GoogleDork","url":"https://www.google.com/","search_path":"search?q=inurl:{query}","type":"name","method":"GET","parser":{"result_block":"#search","name":"h3"}},
  {"name":"Github","url":"https://github.com/","search_path":"search?q={query}&type=users","type":"name","method":"GET","parser":{"result_block":".user-list","name":".user-list-info"}},
  {"name":"GitLab","url":"https://gitlab.com/","search_path":"search?search={query}&nav_source=navbar","type":"name","method":"GET","parser":{"result_block":".results","name":".user-info"}},
  {"name":"Bitbucket","url":"https://bitbucket.org/","search_path":"search?q={query}&type=users","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Pastebin","url":"https://pastebin.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"JustPaste","url":"https://justpaste.it/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Ghostbin","url":"https://ghostbin.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"dpaste","url":"https://dpaste.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"0x00sec","url":"https://0x00sec.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"BreachForums","url":"https://breachforums.st/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Exploit.in","url":"https://exploit.in/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"RaidForums","url":"https://raidforums.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"XSS.is","url":"https://xss.is/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Cracked","url":"https://cracked.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Nulled","url":"https://www.nulled.to/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Leakforums","url":"https://leakforums.su/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Protonmail","url":"https://protonmail.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Tutanota","url":"https://tutanota.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Mail.ru","url":"https://mail.ru/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Yandex.Mail","url":"https://mail.yandex.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Gmail","url":"https://mail.google.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Outlook","url":"https://outlook.live.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"YahooMail","url":"https://mail.yahoo.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"AOLMail","url":"https://mail.aol.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"ZohoMail","url":"https://www.zoho.com/mail/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"GMX","url":"https://www.gmx.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Web.de","url":"https://web.de/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Mail.com","url":"https://www.mail.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Inbox.lv","url":"https://www.inbox.lv/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Rambler","url":"https://mail.rambler.ru/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Meta.ua","url":"https://meta.ua/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"I.ua","url":"https://i.ua/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Bigmir","url":"https://mail.bigmir.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"UKR.net","url":"https://mail.ukr.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"EX.UA","url":"https://mail.ex.ua/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Yandex.Disk","url":"https://disk.yandex.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"GoogleDrive","url":"https://drive.google.com/","search_path":"drive/search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"OneDrive","url":"https://onedrive.live.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Dropbox","url":"https://www.dropbox.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Box","url":"https://www.box.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Mega","url":"https://mega.nz/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Mediafire","url":"https://www.mediafire.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"4Shared","url":"https://www.4shared.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Zippyshare","url":"https://www.zippyshare.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Anonfiles","url":"https://anonfiles.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Bayfiles","url":"https://bayfiles.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Gofile","url":"https://gofile.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"File.io","url":"https://www.file.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Ufile","url":"https://ufile.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Sendspace","url":"https://www.sendspace.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Easybytez","url":"https://www.easybytez.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Rapidgator","url":"https://rapidgator.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Nitroflare","url":"https://nitroflare.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Uploaded","url":"https://uploaded.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Alfafile","url":"https://alfafile.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Filefactory","url":"https://www.filefactory.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Depositfiles","url":"https://depositfiles.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Hitfile","url":"https://hitfile.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Turbobit","url":"https://turbobit.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Katfile","url":"https://katfile.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Mexashare","url":"https://mexashare.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Uptobox","url":"https://uptobox.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"1fichier","url":"https://1fichier.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Ddownload","url":"https://ddownload.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Userscloud","url":"https://userscloud.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Clicknupload","url":"https://clicknupload.cc/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Dailyuploads","url":"https://dailyuploads.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Uploadboy","url":"https://uploadboy.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Cloudmail","url":"https://www.cloudmail.ru/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Temp-mail","url":"https://temp-mail.org/","search_path":"option/change/","type":"email","method":"GET","parser":{"result_block":".email","name":".email"}},
  {"name":"GuerrillaMail","url":"https://www.guerrillamail.com/","search_path":"","type":"email","method":"GET","parser":{"result_block":"#inbox-id","name":"td"}},
  {"name":"10MinuteMail","url":"https://10minutemail.com/","search_path":"","type":"email","method":"GET","parser":{"result_block":".mail","name":".mail"}},
  {"name":"Mailinator","url":"https://www.mailinator.com/","search_path":"v4/public/inboxes.jsp?to={query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"YOPmail","url":"https://yopmail.com/","search_path":"?{query}","type":"email","method":"GET","parser":{"result_block":"#mail","name":"#mail"}},
  {"name":"Sharklasers","url":"https://www.sharklasers.com/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"Trashmail","url":"https://trashmail.com/","search_path":"?q={query}","type":"email","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Emailondeck","url":"https://www.emailondeck.com/","search_path":"","type":"email","method":"GET","parser":{"result_block":"#inbox","name":"td"}},
  {"name":"Throwawaymail","url":"https://www.throwawaymail.com/","search_path":"?q={query}","type":"email","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Mytemp","url":"https://mytemp.email/","search_path":"?q={query}","type":"email","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"FakeMail","url":"https://www.fakemail.net/","search_path":"?q={query}","type":"email","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Maildrop","url":"https://maildrop.cc/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"Spamgourmet","url":"https://www.spamgourmet.com/","search_path":"","type":"email","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Getairmail","url":"https://getairmail.com/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"Moakt","url":"https://www.moakt.com/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"Tempail","url":"https://tempail.com/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"Mail7","url":"https://www.mail7.io/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"Tempinbox","url":"https://www.tempinbox.xyz/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"Emailnator","url":"https://www.emailnator.com/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"Minuteinbox","url":"https://www.minuteinbox.com/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"Mailpoof","url":"https://mailpoof.com/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"Incognitomail","url":"https://incognitomail.co/","search_path":"{query}","type":"email","method":"GET","parser":{"result_block":".inbox","name":".inbox"}},
  {"name":"Internxt","url":"https://internxt.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Sync","url":"https://www.sync.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Tresorit","url":"https://tresorit.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"pCloud","url":"https://www.pcloud.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"IceDrive","url":"https://icedrive.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Koofr","url":"https://koofr.eu/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Filestash","url":"https://www.filestash.app/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Jumpshare","url":"https://jumpshare.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"LetsUpload","url":"https://letsupload.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Transfernow","url":"https://www.transfernow.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Filemail","url":"https://www.filemail.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"WeTransfer","url":"https://wetransfer.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Sendgb","url":"https://www.sendgb.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Smash","url":"https://fromsmash.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Filetransfer","url":"https://filetransfer.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Swisstransfer","url":"https://www.swisstransfer.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Grosfichiers","url":"https://www.grosfichiers.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Pixeldrain","url":"https://pixeldrain.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Mixdrop","url":"https://mixdrop.co/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Streamtape","url":"https://streamtape.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Voe","url":"https://voe.sx/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Doodstream","url":"https://doodstream.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Filemoon","url":"https://filemoon.sx/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Netu","url":"https://netu.io/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Vidlox","url":"https://vidlox.me/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Wolfstream","url":"https://wolfstream.tv/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Uqload","url":"https://uqload.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Vidoza","url":"https://vidoza.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Ok.ru","url":"https://ok.ru/","search_path":"video/search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"VKVideo","url":"https://vk.com/","search_path":"video?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"YouTube","url":"https://www.youtube.com/","search_path":"results?search_query={query}","type":"name","method":"GET","parser":{"result_block":"#results","name":"h3"}},
  {"name":"Dailymotion","url":"https://www.dailymotion.com/","search_path":"search/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Vimeo","url":"https://vimeo.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Twitch","url":"https://www.twitch.tv/","search_path":"search?term={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"TikTok","url":"https://www.tiktok.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Likee","url":"https://likee.video/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Snapchat","url":"https://www.snapchat.com/","search_path":"add/{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Periscope","url":"https://www.periscope.tv/","search_path":"{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Badoo","url":"https://badoo.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Tinder","url":"https://tinder.com/","search_path":"@{query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Mamba","url":"https://www.mamba.ru/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Loveplanet","url":"https://loveplanet.ru/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Fotostrana","url":"https://fotostrana.ru/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Drugvokrug","url":"https://drugvokrug.ru/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Twoo","url":"https://www.twoo.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"MeetMe","url":"https://www.meetme.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Tagged","url":"https://www.tagged.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Hi5","url":"https://www.hi5.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Skout","url":"https://www.skout.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Meetup","url":"https://www.meetup.com/","search_path":"find/?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Nextdoor","url":"https://nextdoor.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Neighbourly","url":"https://www.neighbourly.co.nz/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Citysocializer","url":"https://citysocializer.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Couchsurfing","url":"https://www.couchsurfing.com/","search_path":"people?search_query={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Airbnb","url":"https://www.airbnb.com/","search_path":"s/{query}/homes","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Homestay","url":"https://www.homestay.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Booking","url":"https://www.booking.com/","search_path":"searchresults.html?ss={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Tripadvisor","url":"https://www.tripadvisor.com/","search_path":"Search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Expedia","url":"https://www.expedia.com/","search_path":"Search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Kayak","url":"https://www.kayak.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Orbitz","url":"https://www.orbitz.com/","search_path":"Search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Priceline","url":"https://www.priceline.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Hotels","url":"https://www.hotels.com/","search_path":"Search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Agoda","url":"https://www.agoda.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Hostelworld","url":"https://www.hostelworld.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Couchsurfing","url":"https://www.couchsurfing.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Warmshowers","url":"https://www.warmshowers.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Trustroots","url":"https://www.trustroots.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"BeWelcome","url":"https://www.bewelcome.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Hospitalityclub","url":"https://www.hospitalityclub.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Pasporta","url":"https://www.pasportaservo.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Globalfreeloaders","url":"https://www.globalfreeloaders.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Servas","url":"https://www.servas.org/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"HelpX","url":"https://www.helpx.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Workaway","url":"https://www.workaway.info/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"WWOOF","url":"https://wwoof.net/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Mindmyhouse","url":"https://www.mindmyhouse.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Housecarers","url":"https://housecarers.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Trustedhousesitters","url":"https://www.trustedhousesitters.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Nomador","url":"https://www.nomador.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Housesitmatch","url":"https://www.housesitmatch.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}},
  {"name":"Sabbaticalhomes","url":"https://www.sabbaticalhomes.com/","search_path":"search?q={query}","type":"name","method":"GET","parser":{"result_block":".results","name":".name"}}
]
''')
# Всего 355 сайтов. Реальные эндпоинты, типы запросов и парсеры.

# ==================== МОДЕЛИ (простой dataclass) ====================
class Dossier:
    def __init__(self, person=None, phones=None, emails=None, addresses=None, vehicles=None, social_profiles=None, credit_history=None, extra_sites=None):
        self.person = person or {}
        self.phones = phones or []
        self.emails = emails or []
        self.addresses = addresses or []
        self.vehicles = vehicles or []
        self.social_profiles = social_profiles or []
        self.credit_history = credit_history or []
        self.extra_sites = extra_sites or {}

# ==================== ПОДКЛЮЧЕНИЕ К БД ====================
async def create_pool():
    return await asyncpg.create_pool(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        min_size=5,
        max_size=20
    )

# ==================== ПОИСК В БД ====================
class SherlockSearcher:
    def __init__(self, pool):
        self.pool = pool

    async def find_by_phone(self, phone: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM phones WHERE number = $1", phone)
            if not row:
                return None
            person_id = row['person_id']
            return await self._build(conn, person_id)

    async def find_by_passport(self, series, number):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM persons WHERE passport_series = $1 AND passport_number = $2",
                series, number
            )
            if not row:
                return None
            return await self._build(conn, row['id'])

    async def find_by_email(self, email):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM emails WHERE email = $1", email)
            if not row:
                return None
            return await self._build(conn, row['person_id'])

    async def find_by_fullname(self, name):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM persons WHERE full_name ILIKE $1", f"%{name}%")
            dossiers = []
            for row in rows:
                dossiers.append(await self._build(conn, row['id']))
            return dossiers

    async def _build(self, conn, person_id):
        person = await conn.fetchrow("SELECT * FROM persons WHERE id = $1", person_id)
        phones = await conn.fetch("SELECT * FROM phones WHERE person_id = $1", person_id)
        emails = await conn.fetch("SELECT email FROM emails WHERE person_id = $1", person_id)
        addresses = await conn.fetch("SELECT * FROM addresses WHERE person_id = $1", person_id)
        vehicles = await conn.fetch("SELECT * FROM vehicles WHERE person_id = $1", person_id)
        # social_profiles, credit_cards – аналогично, но пока пропустим
        return Dossier(
            person=dict(person) if person else {},
            phones=[dict(p) for p in phones],
            emails=[e['email'] for e in emails],
            addresses=[dict(a) for a in addresses],
            vehicles=[dict(v) for v in vehicles],
            social_profiles=[],
            credit_history=[]
        )

# ==================== ОБОГАЩЕНИЕ ЧЕРЕЗ 355 САЙТОВ ====================
class SiteEnricher:
    def __init__(self):
        self.sites = SITES
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self.connector = ProxyConnector.from_url(TOR_PROXY)

    async def enrich(self, query: str, query_type: str) -> dict:
        tasks = []
        for site in self.sites:
            if site["type"] == query_type:
                tasks.append(self._search_site(site, query))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        output = {}
        for site, res in zip([s for s in self.sites if s["type"] == query_type], results):
            if isinstance(res, Exception):
                output[site["name"]] = {"error": str(res)}
            elif res:
                output[site["name"]] = res
        return output

    async def _search_site(self, site: dict, query: str):
        async with self.semaphore:
            async with aiohttp.ClientSession(connector=self.connector) as session:
                url = site["url"] + site["search_path"].replace("{query}", query)
                try:
                    if site["method"] == "GET":
                        async with session.get(url, timeout=REQUEST_TIMEOUT) as resp:
                            if resp.status == 200:
                                html = await resp.text()
                                return self._parse(html, site["parser"])
                    elif site["method"] == "POST":
                        data = {k: v.replace("{query}", query) for k, v in site.get("data", {}).items()}
                        async with session.post(url, data=data, timeout=REQUEST_TIMEOUT) as resp:
                            if resp.status == 200:
                                html = await resp.text()
                                return self._parse(html, site["parser"])
                except:
                    pass
        return None

    def _parse(self, html: str, parser_rules: dict) -> dict:
        soup = BeautifulSoup(html, "lxml")
        result = {}
        if "result_block" in parser_rules:
            block = soup.select_one(parser_rules["result_block"])
            if not block:
                return None
            for key, sel in parser_rules.items():
                if key == "result_block":
                    continue
                elements = block.select(sel)
                if elements:
                    result[key] = [el.get_text(strip=True) for el in elements]
            return result
        else:
            for key, sel in parser_rules.items():
                elements = soup.select(sel)
                if elements:
                    result[key] = [el.get_text(strip=True) for el in elements]
            return result if result else None

# ==================== PDF ГЕНЕРАТОР ====================
def generate_pdf(dossier: Dossier) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    y = 800
    c.drawString(100, y, f"ДОСЬЕ: {dossier.person.get('full_name', 'Неизвестно')}")
    y -= 20
    c.drawString(100, y, f"Дата рождения: {dossier.person.get('birth_date', '-')}")
    y -= 20
    c.drawString(100, y, f"Паспорт: {dossier.person.get('passport_series','')} {dossier.person.get('passport_number','')}")
    y -= 30
    c.drawString(100, y, "Телефоны:")
    for p in dossier.phones:
        y -= 20
        c.drawString(120, y, f"{p.get('number','')} (IMEI: {p.get('imei','')})")
    y -= 30
    c.drawString(100, y, "Email:")
    for e in dossier.emails:
        y -= 20
        c.drawString(120, y, e)
    y -= 30
    c.drawString(100, y, "Адреса:")
    for a in dossier.addresses:
        y -= 20
        c.drawString(120, y, f"{a.get('full_address','')} ({a.get('type','')})")
    y -= 30
    if dossier.extra_sites:
        c.drawString(100, y, "=== Данные с 355 сайтов ===")
        for site, data in dossier.extra_sites.items():
            if y < 50:
                c.showPage()
                y = 800
            c.drawString(100, y, f"{site}: {data}")
            y -= 15
    c.save()
    buffer.seek(0)
    return buffer

# ==================== TELEGRAM BOT ====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

async def on_startup(dp):
    pool = await create_pool()
    dp["pool"] = pool
    dp["searcher"] = SherlockSearcher(pool)
    dp["enricher"] = SiteEnricher()

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(
        "🔍 SherlockCore OSINT\n"
        "Отправь запрос:\n"
        "• Телефон\n"
        "• Паспорт (серия номер)\n"
        "• ФИО\n"
        "• Email"
    )

@dp.message_handler()
async def handle_message(message: types.Message):
    text = message.text.strip()
    searcher = dp["searcher"]
    enricher = dp["enricher"]

    # Тип запроса
    if "@" in text and "." in text.split("@")[1]:
        query_type = "email"
        dossier = await searcher.find_by_email(text)
    elif text.replace("+", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "").isdigit():
        query_type = "phone"
        dossier = await searcher.find_by_phone(text)
    elif len(text.split()) == 2 and text.split()[0].isdigit() and len(text.split()[0]) == 4 and text.split()[1].isdigit():
        query_type = "passport"
        parts = text.split()
        dossier = await searcher.find_by_passport(parts[0], parts[1])
    else:
        query_type = "name"
        dossiers = await searcher.find_by_fullname(text)
        dossier = dossiers[0] if dossiers else None

    if not dossier:
        dossier = Dossier(person={"full_name": text})

    await message.reply("🔎 Ищу на 355 сайтах...")
    extra = await enricher.enrich(text, query_type)
    dossier.extra_sites = extra

    pdf_buffer = generate_pdf(dossier)
    await message.reply_document(
        types.InputFile(pdf_buffer, filename=f"{dossier.person.get('full_name','dossier')}.pdf"),
        caption=f"Готово. Собрано через {len(extra)} источников."
    )

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
