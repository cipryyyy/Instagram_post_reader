import discord
from discord.ext import tasks
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException as NSEE
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from termcolor import colored
from random import random
from random import randint
import requests
import time
import datetime
import os
import traceback
import sys
import urllib.request
import asyncio

client=discord.Client()
account=
cnt=0
pth= PATH
news_path= PATH
bin_folder= PATH
announce_folder= PATH
authorized= PATH
sleeping=False

BCP=pth+"bcp.txt"
IDF=pth+"channel_id.txt"
BLG=pth+"bots_log.txt"

if os.path.isfile(BCP)==True:
    src=open(BCP,"r")
    last_link=src.read()
    src.close()
else:
    print("No backup file, quitting")
    quit()
if os.path.isfile(IDF)==True:
    id_src=open(IDF,"r")
    content=id_src.readlines()
    id_channel=int(content[0])
    id_programmer=int(content[1])
    id_news=int(content[2])
    id_src.close()
else:
    print("No ID file, quitting")
    quit()
if os.path.isfile(BLG)==False:
    print("No log file, quitting")
    quit()

def Log(type, msg):
    types=["SYSTEM","POST","SECURITY","BUG","QUERY"]

    report=f"[{datetime.datetime.now()}] {types[type]} -> {msg}\n"
    with open(BLG, "a") as f:
        f.write(report)
        f.close()

async def Main(id_channel=id_channel):
    await client.wait_until_ready()
    print(colored("BOTTINO_UPDATE: main function is ready!","yellow"))
    Log(0,"main function loaded")
    global last_link
    global pth
    global cnt
    global sleeping
    global BLG
    global account
    global authorized

    last_code=None
    channel=client.get_channel(id_channel)

    def DataGen(source):
        TW=None
        AW=None
        author=""
        text=[]
        hashtags=[]

        words=source.split()
        for word in words:
            if word[0]=="#":
                hashtags.append(word)
            if "quot" in word:
                if TW==True:
                    TW=False
                else:
                    TW=True
            if TW==True:
                text.append(word.replace("&quot;"," "))
            if word=="by":
                AW=True
            if word=="in" or word=="on":
                AW=False
            if AW==True:
                author+=word+" "

        author=author.replace("by ","")
        text=" ".join(text)
        if len(hashtags)==0:
            hashtags=["No hashtags used"]
        if text=="":
            text="No text in the image"
        return author, hashtags, text

    def LinkGen(source):
        href=source.split()[1]
        partial_link=href[6:-1]
        return partial_link

    try:
        while True:
            hour=int(datetime.datetime.now().strftime("%H"))
            if hour<9 or hour>=22:
                if sleeping==False:
                    await client.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name=authorized))
                    print(colored("+++NIGHT MODE STARTED+++","yellow","on_red"))
                    sleeping=True
                    Log(0,"night mode started")

            else:
                if sleeping==True:
                    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=account))
                    print(colored("+++NIGHT MODE ENDED+++","yellow","on_red"))
                    sleeping=False
                    cnt=0
                    Log(0,"night mode ended")
            if sleeping==False:
                cnt+=1
                page_link="https://www.instagram.com/{}/".format(account.replace("@",""))
                options=Options()
                options.add_argument("--headless")
                browser=webdriver.Firefox(options=options, executable_path="/usr/local/bin/geckodriver_v0.28")
                browser.get(page_link)

                code=browser.find_element_by_class_name("v1Nh3.kIKUG._bz0w").get_attribute('outerHTML')
                tags=code.replace("><",">(SEP)<").split(sep="(SEP)")
                for tag in tags:
                    if tag.startswith("<img"):
                        author, htag, text=DataGen(tag)
                    if tag.startswith("<a"):
                        link="https://www.instagram.com"+LinkGen(tag)
                browser.get(link)
                caption_raw=browser.find_element_by_class_name("C4VMK").get_attribute('innerHTML')
                soup=BS(caption_raw, "html.parser")
                full_caption=soup.find("span").get_text().split()
                caption=""
                for i in full_caption:
                    if not "#" in i:
                        caption+=i+" "

                if len(caption.split())>40:
                    caption=" ".join(caption.split()[:40])+"..."
                browser.quit()

                if link!=last_link:
                    Log(1,f"New post ({str(link)})")
                    print(colored(f"[{datetime.datetime.now()}]###!NEW POST!###","green"))

                    last_link=link
                    backup=open(BCP,"w")
                    backup.write(last_link)
                    backup.close()

                    options=Options()
                    options.headless=True
                    driver = webdriver.Firefox(options=options, executable_path="/usr/local/bin/geckodriver_v0.28")
                    driver.set_page_load_timeout(180)

                    name="file.png"

                    try:
                        driver.get(link)
                        soup = BS(driver.page_source, 'lxml')
                        img = soup.find('img', class_='FFVAD')
                        img_url = img['src']
                        r = requests.get(img_url)
                        with open(pth+name,'wb') as f:
                            f.write(r.content)

                    except TypeError:
                        driver.get(link)
                        code=driver.find_element_by_class_name("tWeCl").get_attribute("outerHTML")
                        url=code.split()[-4].replace("&amp;","&")[8:-1]
                        r = urllib.request.urlopen(url)
                        with open(pth+name,"wb") as f:
                            f.write(r.read())
                    driver.close()
                    comm=f"@everyone NUOVO POST\n{account}\n{caption}\n\nLINK AL POST:\n{link}"
                    await channel.send(comm, file=discord.File(pth+name))
                if cnt==6:
                    Log(0,"BREAK")
                    cnt=0
                    await asyncio.sleep(randint(4,20)*60)
                await asyncio.sleep(15*60+random()*180)
            else:
                await asyncio.sleep(120)

    except Exception:
        print(colored("An error occured, check logs for further infos","red"))
        exc_info=sys.exc_info()
        err=traceback.format_exception(*exc_info)
        Log(3,str(err[-1]).replace("\n",""))
        quit()

async def News():
    global news_path
    global bin_folder
    global id_news
    global authorized

    work=True
    channel=client.get_channel(id_news)
    incipit="@everyone\n"
    patch="\n\nFornito da <https://t.me/notiziae>"
    existing=os.listdir(bin_folder)

    await client.wait_until_ready()
    print(colored("BOTTINO_UPDATE: news function is ready!","yellow"))
    Log(0,"news function loaded")

    while True:

        try:
            if len(os.listdir(news_path))!=0:
                for file in os.listdir(news_path):
                    splitted_name=file.split(sep=".")
                    basename=splitted_name[0]
                    extension=splitted_name[1]

                    msg_type=basename.split(sep="_")[0]
                    channel_name=basename.split(sep="_")[1].replace(" ","")
                    index=basename.split(sep="_")[2]
                    edited=basename.split(sep="_")[3]

                    if channel_name!=authorized:
                        print(colored(f"SECURITY: {channel_name} tried to send messages to BOTtino","red"))
                        Log(2,f"{channel_name} tried to send message")
                        os.remove(news_path+file)
                        continue

                    if file in existing:
                        os.remove(news_path+file)
                        continue

                    if edited=="original":
                        Log(1,f"news indexed {index} published")

                        if msg_type=="message":
                            with open(news_path+file,"r") as f:
                                message = await channel.send(incipit+f.read().replace("@notiziae","<https://t.me/notiziae>"))
                                f.close()
                                os.replace(f"{news_path}{file}", f"{bin_folder}{index}_{message.id}.txt")

                        else:
                            if msg_type!="caption":
                                caption_file=f"{news_path}caption_{channel_name}_{index}_{edited}.txt"
                                if os.path.exists(caption_file)==True:
                                    caption=open(caption_file,"r")
                                    message = await channel.send(incipit+caption.read().replace("@notiziae","<https://t.me/notiziae>"), file=discord.File(f"{news_path}{file}"))
                                    caption.close()
                                    os.replace(caption_file, f"{bin_folder}{index}_{message.id}.txt")      #caption migration
                                    os.replace(f"{news_path}{file}", f"{bin_folder}{file}")                #file migration
                                else:

                                    message = await channel.send(incipit+patch, file=discord.File(f"{news_path}{file}"))
                                    os.remove(f"{news_path}{file}")
                    else:
                        Log(1,f"news indexed {index} edited")

                        for deleted_file in os.listdir(bin_folder):
                            splitted_name=deleted_file.split(sep=".")
                            basename=splitted_name[0]
                            extension=splitted_name[1]


                            if extension=="txt":
                                fetch_index=basename.split(sep="_")[0]
                                msg_id=basename.split(sep="_")[1]

                            try:
                                fetch_index=int(fetch_index)
                                work=True
                            except ValueError:
                                work=False

                            if work:
                                try:
                                    if int(fetch_index)==int(index):
                                        target = await channel.fetch_message(int(msg_id))
                                        edit=open(news_path+file,"r")
                                        await target.edit(content=incipit+edit.read().replace("@notiziae","<https://t.me/notiziae>"))
                                        edit.close()
                                        os.remove(news_path+file)

                                except FileNotFoundError:
                                    continue
            await asyncio.sleep(5)

        except Exception:
            print(colored("An error occured, check logs for further infos","red"))
            exc_info=sys.exc_info()
            err=traceback.format_exception(*exc_info)
            Log(3,str(err[-1]).replace("\n",""))

            quit()

async def Announce(id_channel=id_channel):
    global announce_folder
    channel=client.get_channel(id_channel)

    print(colored("BOTTINO_UPDATE: announce function is ready!","yellow"))
    Log(0,"announce function loaded")

    while true:
        for file in os.listdir(announce_folder):
            with open(announce_folder+file,"w") as f:
                channel.send(f.read())
                Log(1,"announce published")
            os.remove(announce_folder+file)
        await asyncio.sleep(5)

def starter():
    client.loop.create_task(Main())
    client.loop.create_task(News())
    client.loop.create_task(Announce())

@client.event
async def on_ready():
    global id_channel
    Log(0,f"BOT ONLINE")
    print(colored(f"Logged in as {client.user.name} [{client.user.id}]","cyan"))
    starter()
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=account))

@client.event
async def on_message(msg):
    chid=int(str(msg).split()[3][3:])
    channel=client.get_channel(chid)
    if client.user.id!=msg.author.id:
        if msg.content.lower()==".link" or msg.content.lower()=="/link":
            Log(4,"link")
            global last_link
            global account
            facebook=LINK
            telegram=LINK
            page_link="https://www.instagram.com/{}/".format(account.replace("@",""))

            links= f"Instagram:   <{page_link}>\n"
            links+=f"Facebook:    <{facebook}>\n"
            links+=f"Telegram:    <{telegram}>\n"
            links+=f"Ultimo post: <{last_link}>"
            await channel.send(f"{msg.author.mention} LINK UTILI:\n{links}")

client.run(TOKEN)
