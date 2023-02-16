# -*- coding: utf-8 -*-

from __future__ import unicode_literals

# noinspection PyUnresolvedReferences
from codequick import Route, Resolver, Listitem, utils, run
from codequick.utils import urljoin_partial, bold
import urlquick
import xbmcgui
import xbmcaddon
from . import logger #logger.debug(FUNCION O VARIABLE A DEBUGUEAR)
from . import tools
import re
import resolveurl
import xbmc
import urllib
import xbmcvfs
import os
from time import sleep as wait
import shutil

skin = xbmc.getSkinDir()
xmls_route = [
    {"xmls": "xml"},
    {"xmls": "16x9"},
    {"xmls": "720p"},
    {"xmls": "1080i"},
]
# Conocer que Skin estamos usando y obtener las rutas
for xmls_folder in xmls_route:
    xmls = xbmcvfs.translatePath('special://home/addons/{}/{}/'.format(skin,xmls_folder["xmls"]))
    skin_original = xbmcvfs.translatePath('special://xbmc/addons/{}'.format(skin))
    skin_new = xbmcvfs.translatePath('special://home/addons/{}'.format(skin))
    act_font = xmls + 'Font.xml'
    xml_font = xbmcvfs.translatePath('special://home/addons/plugin.video.ariyasumomoka/resources/lib/Font.xml')
    
    if xbmcvfs.exists(xmls):   

        # Leer el archivo Font.xml
        with open(act_font, "r") as f:
            data = f.readlines()
            line_org = data[2]
            line_need = '<fontset id="Default" idloc="31053">'
                
            # Verificar si la linea 3 es la correcta
            if line_org.strip() != line_need.strip():
                # Si la linea no es correcta, eliminar y reemplazar el archivo Font.xml
                xbmcvfs.delete(act_font)
                shutil.copy(xml_font, act_font.replace('Font.xml',''))
                xbmcgui.Dialog().ok("30002", "30003")
            else:
                # Si la linea es correcta, no hacer nada
                pass

    elif not xbmcvfs.exists(xmls):
        # Si no existe la carpeta, verificar si estamos usando Estuary o Estouchy
        if skin == "skin.estuary" or skin == "skin.estouchy":
            try:
                # Copiar la carpeta original y reemplazar el archivo Font.xml
                shutil.copytree(skin_original, skin_new)
                xbmcvfs.delete(xbmcvfs.translatePath('{}{}'.format(skin_new,'/xml/Font.xml')))
                shutil.copy(xml_font, '{}/xml/'.format(skin_new))
                xbmcgui.Dialog().ok("30002", "30003")
            except OSError as error:
                logger.debug(error)
    else:
        xbmcgui.Dialog().ok("30004" , "30005")


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
}
URL = "https://www.ariyasumomoka.jp"
url_constructor = urljoin_partial(URL)
s = urlquick.Session()

@Route.register
def root(plugin, content_type="segment"):
    menu_items = [
        {"label": "PHOTOGRAPHY", "callback": get_photos, "linkpart": "/photography/"},
        {"label": "MOVIE", "callback": get_videos, "linkpart": "/movie/"},
        {"label": "DISCOGRAPHY", "callback": get_albums, "linkpart": "/discography/"},
    ]
    
    for item_data in menu_items:
        item = Listitem()
        item.label = item_data["label"]
        url = url_constructor(item_data["linkpart"])
        item.set_callback(item_data["callback"], url=url)
        yield item

   
@Route.register
def get_videos(plugin, url):
    resp = s.get(url, headers=headers, max_age=-1)
    videosRoot = resp.parse("ul", attrs={"class": "movie-index"})
    videoslist = videosRoot.iterfind("li/a")

    for elem in videoslist:
        item = Listitem()
        item.label = elem.find("div").text
        linkpart = elem.get("href")
        url = url_constructor("/movie/" + linkpart)
        img = elem.find("figure/img").get("src")
        item.art["thumb"] = url_constructor(img)
        item.art["fanart"] = url_constructor(img)
        item.set_callback(play_Video, url=url)
        yield item
        
        
@Route.register
def get_photos(plugin, url):
    resp = s.get(url, headers=headers, max_age=-1)
    photosRoot = resp.parse("ul", attrs={"class": "bio__content-list"})
    photoslist = photosRoot.iterfind("li/img")
    
    for photo in photoslist:
        url = url_constructor(photo.get("src"))
        url = s.get(url)
        route = "special://home/temp"
        profile = xbmcvfs.translatePath(route)
        directory = "ariyasumomoka"
        gallery = resp.url.replace('https://www.ariyasumomoka.jp/','').replace('/','')
        path = xbmcvfs.translatePath(os.path.join(profile, directory, gallery))
        try:
            xbmcvfs.mkdirs(path)
            logger.debug("Directory '%s' created" %directory)
        except OSError as error:
            logger.debug(error)

        
        img = url.url.replace('https://www.ariyasumomoka.jp/images/bio/','')
        img_path = xbmcvfs.translatePath("{}/{}/{}/{}".format(profile,directory, gallery, img))
        image = open(img_path, 'wb')
        image.write(url.content)
        image.close()
        image_file = img_path
        
        item = Listitem()
        item.label = img.replace('.jpg','')
        album = xbmcvfs.translatePath("{}/{}/{}".format(profile,directory, gallery))
        pic = xbmcvfs.translatePath("{}/{}/{}/{}".format(profile,directory, gallery, img))
        
        item.art["thumb"] = image_file
        item.art["fanart"] = image_file
        item.set_callback(show_Photos, album=album, pic=pic, url=url.url)
        yield item


@Resolver.register
def play_Video(plugin, url):
    _url = url
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}
    resp = s.get(url, headers=headers)
    page_root = resp.parse("div", attrs={"class":"wrap"})
    page_elems = page_root.iterfind("div")

    for elem in page_elems:
        url = elem.find("div/div/iframe").get("src")

        try:
            resolved = resolveurl.resolve(url)
            return resolved
        except urllib.error.HTTPError as error:
            if error.code == 403:
                _url = _url.lower()
                xbmcgui.Dialog().ok("30009", "30010{}".format(_url))
                xbmc.executebuiltin('Dialog.Close(all,true)')
            else:
                pass
        

@Resolver.register
def show_Photos(plugin,album,pic,url):
    album = album
    url = url
    xbmc.executebuiltin("ShowPicture({})".format(pic))
    wait(5)
    xbmc.executebuiltin("SlideShow({})".format(album))
    plugin = plugin.extract_source(url)
    return Listitem().from_dict(**{
        "label" : "Showing",
        "callback" : plugin,
    })


@Route.register
def get_albums(plugin,url):
    resp = s.get(url, headers=headers, max_age=-1)
    albumsRoot = resp.parse("div", attrs={"class": "wrap"})
    albumslist = albumsRoot.iterfind("ul")
    
    for elem in albumslist:
        album_info = [
            {"label": elem.find("li/span").text, "linkpart": "/discography/"},
            {"label": elem.find("li/a").text, "linkpart": elem.find("li/a").get("href")},
            {"label": elem.find("li[3]/a").text, "linkpart": elem.find("li[3]/a").get("href")},
            {"label": elem.find("li[4]/a").text, "linkpart": elem.find("li[4]/a").get("href")},
            {"label": elem.find("li[5]/a").text, "linkpart": elem.find("li[5]/a").get("href")},
            {"label": elem.find("li[6]/a").text, "linkpart": elem.find("li[6]/a").get("href")},
            ]
            
        for album in album_info:
            item = Listitem()
            item.label = album["label"]
            linkpart = album["linkpart"]
            url = url_constructor(linkpart)
            item.set_callback(albums_List, url=url)
            yield item
        

@Route.register
def albums_List(plugin, url):
    resp = s.get(url, headers=headers, max_age=-1)
    try:
        albumsRoot = resp.parse("div", attrs={"class": "disco-index__list"})
        albumslist = albumsRoot.iterfind("ul/li/a")
        
        for album in albumslist:
            item = Listitem()
            item.label = album.find("div[2]").text
            linkpart = album.get("href").replace('.','/discography/')
            url = url_constructor(linkpart)
            img = album.find("figure/img").get("src")
            item.art["thumb"] = url_constructor(img)
            item.art["fanart"] = url_constructor(img)
            item.set_callback(album_Page, url=url)
            yield item
    except RuntimeError as error:
        xbmcgui.Dialog().ok("30011", "30012")
        xbmc.executebuiltin('Dialog.Close(all,true)')
        
        
        
@Route.register
def album_Page(plugin, url):
    resp = s.get(url, headers=headers, max_age=-1)
    albumRoot = resp.parse("div", attrs={"class": "wrap"})
    albumElems = albumRoot.iterfind("div/div")
    
    for elem in albumElems:
        item = Listitem()
        item.label = elem.find("div[2]/h3").text
        url = elem.find("div[2]/div[3]/a[2]").get("href")
        img = elem.find("div/div/div/img").get("src")
        item.art["thumb"] = url_constructor(img)
        item.art["fanart"] = url_constructor(img)
        if item.label == "有安杏果 Pop Step Zepp Tour 2019":
            item.set_callback(enter_AlbumPopSZT2019, url=url)
        else:
            item.set_callback(enter_AlbumVideo, url=url)
    
        yield item
        
        
@Route.register
def enter_AlbumVideo(plugin, url):
    resp = s.get(url, headers=headers, max_age=-1)
    videosRoot = resp.parse("section", attrs={"class": "section section--v1"})
    videosElems = videosRoot.iterfind("div/div/div/div/div/iframe")
    
    counter = 1
    for elem in videosElems:
        item = Listitem()
        item.label = "30013" + str(counter)
        url = elem.get("src")
        item.set_callback(play_AlbumVideo, url=url)
        counter += 1
        yield item        
        
            
@Route.register
def enter_AlbumPopSZT2019(plugin, url):
    resp = s.get(url, headers=headers, max_age=-1)
    videosRoot = resp.parse("div", attrs={"class": "movie"})
    videosElems = videosRoot.iterfind("div/div/div/iframe")
    
    counter = 1
    for elem in videosElems:
        item = Listitem()
        item.label = "30013" + str(counter)
        url = elem.get("src")
        item.set_callback(play_AlbumVideo, url=url)
        counter += 1
        yield item
        

@Resolver.register
def play_AlbumVideo(plugin, url):
    url = url
    resolved = resolveurl.resolve(url)
    return resolved
