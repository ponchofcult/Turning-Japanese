# -*- coding: utf-8 -*-

from __future__ import unicode_literals

# noinspection PyUnresolvedReferences
from codequick import Route, Resolver, Listitem, utils, run
from codequick.utils import urljoin_partial, bold
import urlquick
import xbmcgui
import re
import resolveurl
import xbmc
import urllib

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
}
URL = "https://hustlepress.co.jp"
LOGIN_ROUTE = ""

#Addon Start    
@Route.register
def root(plugin, content_type="segment"):
    item = Listitem()
    item.label = "HOME"
    linkpart = "/"
    url = URL + linkpart
    item.set_callback(get_postlist, url=url)  
    yield item
        
    item = Listitem()
    item.label = "GRAVURE"
    linkpart = "/category/gravure/"
    url = URL + linkpart
    item.set_callback(get_postlist, url=url)  
    yield item
        
    item = Listitem()
    item.label = "INTERVIEW"
    linkpart = "/category/interview/"
    url = URL + linkpart
    item.set_callback(get_postlist, url=url)  
    yield item
    
    item = Listitem()
    item.label = "FEATURE"
    linkpart = "/category/feature/"
    url = URL + linkpart
    item.set_callback(get_postlist, url=url)  
    yield item
    
    item = Listitem()
    item.label = "COLUMN"
    linkpart = "/category/coumn/"
    url = URL + linkpart
    item.set_callback(get_postlist, url=url)  
    yield item


@Route.register
def get_postlist(plugin, url):
    resp = urlquick.get(url, headers=headers, max_age=-1)
    postlistRoot = resp.parse("div",attrs={"class":"blogposts-wrapper clearfix"})
    postList = postlistRoot.iterfind("div/ul/li/div/a")
    
    for post in postList:
        item = Listitem()
        item.label = post.get("title")
        url = post.get("href")
        item.art["thumb"] = post.find("img").get("src")
        item.art["fanart"] = post.find("img").get("src")
        item.set_callback(categories, url=url)
        yield item
        
    NextPageTree = resp.parse("div",attrs={"id":"blocks-left"})
    for page in NextPageTree.iterfind("div[@class='pagination clearfix']"):
        a_number = page.find("a").text
        span_number = page.find("span[@aria-current='page']").text
        a = int(a_number)
        span = int(span_number)
        span_menos_uno = span - 1
        if a == span + 1:
            nextPageP = page.find("a")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)
        elif a == span - 1:
            nextPageP = page.find("a[2]")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)
        elif a == span - 2:
            nextPageP = page.find("a[3]")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)    
        elif a == span - 3:
            nextPageP = page.find("a[4]")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)    
        elif a == span - span_menos_uno:
            nextPageP = page.find("a[4]")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)
        else:
            nextPageP = page.find("a[4]")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)     
              

@Route.register
def get_Nextpostlist(plugin,nextPage):
    resp = urlquick.get(nextPage, headers=headers, max_age=-1)
    postlistRoot = resp.parse("div",attrs={"class":"blogposts-wrapper clearfix"})
    postList = postlistRoot.iterfind("div/ul/li/div/a")
    
    for post in postList:
        item = Listitem()
        item.label = post.get("title")
        url = post.get("href")
        item.art["thumb"] = post.find("img").get("src")
        item.art["fanart"] = post.find("img").get("src")
        item.set_callback(categories, url=url)
        yield item
        
    NextPageTree = resp.parse("div",attrs={"id":"blocks-left"})
    for page in NextPageTree.iterfind("div[@class='pagination clearfix']"):
        a_number = page.find("a").text
        span_number = page.find("span[@aria-current='page']").text
        a = int(a_number)
        span = int(span_number)
        span_menos_uno = span - 1
        if a == span + 1:
            nextPageP = page.find("a")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)
        elif a == span - 1:
            nextPageP = page.find("a[2]")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)
        elif a == span - 2:
            nextPageP = page.find("a[3]")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)    
        elif a == span - 3:
            nextPageP = page.find("a[4]")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)    
        elif a == span - span_menos_uno:
            nextPageP = page.find("a[4]")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)
        else:
            nextPageP = page.find("a[4]")
            yield Listitem.next_page(nextPage=nextPageP.get("href"),callback=get_Nextpostlist)
        

@Route.register
def categories(plugin,url):
        item = Listitem()
        item.label = "IMAGES"
        url = url
        item.set_callback(images_List, url=url)
        yield item
        
        item = Listitem()
        item.label = "VIDEOS"
        url = url
        item.set_callback(videos_List, url=url)
        yield item
        
        
@Route.register
def images_List(plugin,url):
    resp = urlquick.get(url, headers=headers, max_age=-1)
    imagesRoot = resp.parse("div",attrs={"class":"post-content"})
    images_list = imagesRoot.iterfind("div/div[3]/p/a/img")
    
    counter = 1
    for image in images_list:
        item = Listitem()
        item.label = "IMAGE " + str(counter)
        url = image.get("src")
        item.art["thumb"] = image.get("src")
        item.art["fanart"] = image.get("src")
        item.set_callback(show_Images, url=url)
        counter += 1
        yield item
        

@Route.register
def videos_List(plugin,url):
    resp = urlquick.get(url, headers=headers, max_age=-1)
    videosRoot = resp.parse("div",attrs={"class":"post-content"})
    videos_list = videosRoot.iterfind("div/div[3]/div/iframe")
    videos_name = videosRoot.iterfind("div/div[3]/h5")
    # counter = 1
    for name,video in zip(videos_name,videos_list):
        item = Listitem()
        item.label = name.text #+ str(counter)
        url = video.get("src")
        # item.art["thumb"] = video.get("src")
        # item.art["fanart"] = video.get("src")
        item.set_callback(play_Video, url=url)
        # counter += 1
        yield item
    
              
@Resolver.register
def show_Images(plugin,url):
    url = url
    xbmc.executebuiltin('ShowPicture(' + url + ')')
    plugin = plugin.extract_source(url)   
    return Listitem().from_dict(**{
        "label" : "Playing",
        "callback" : plugin,
    })       


@Resolver.register
def play_Video(plugin,url):
    url = url        
    resolved = resolveurl.resolve(url)
    return resolved
