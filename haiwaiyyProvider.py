# -*- coding: utf-8 -*-

from provider import *
import utils
import xbmcplugin
from xbmc import Keyboard
import xbmc

class HaiwaiyyProvider(Provider):
    def __init__(self):
        Provider.__init__(self)
        self._header = utils.custom_header("www.haiwaiyy.com", "http", "http://www.haiwaiyy.com/")
        self._baseUrl = "http://www.haiwaiyy.com"
        self._name = "haiwaiyy"
        if len(self._cookie_string) > 0:
            self._header['Cookie'] = self._cookie_string
        if len(self._user_agent) > 0:
            self._header['User-Agent'] = self._user_agent
        
    def index(self):
        # scraper = cfscrape.create_scraper()
        # response = scraper.get(self._baseUrl)
        # result = response.content
        # cookie_string = scraper.cookie_string()
        # user_agent = scraper.headers["User-Agent"]

        for item,value in {"movie": "movie", "tv":"tv", "search": "load_search"}.iteritems():
            listitem=xbmcgui.ListItem(item)
            isFolder=True
            url = self.gen_plugin_url({"act": value,
                                       "name": value})
            xbmcplugin.addDirectoryItem(self._handle,url,listitem,isFolder)
        xbmcplugin.endOfDirectory(self._handle)
        
    def list(self):
        url = self._params['url']
        self.getMovieList(url)
        
    def page_url(self, id, pageno):
        return "/vod-type-id-" + str(id) + "-pg-" + str(pageno) + ".html"
           
    def getMovieList(self, url):
        print url
        urlReg = r'vod-type-id-(\d*)-pg-(\d*)\.html'
        url_result = re.compile(urlReg).findall(url)[0]
        type_id = url_result[0]
        pageno = url_result[1]
        print url_result
        
        next_pageno = str(int(pageno) + 1)
        
        url = self._baseUrl + url
        print("getMoveList url", url)
        #print self._header
        
        
        req = urllib2.Request(url, None, self._header)
        result = self._opener.open(req).read()
        #print result
        #reg = r'<a href="([-a-zA-Z0-9@:%_\+.~#?&//=]*?)" class=".*?">\n<img.*?data-original="(.*?)".*?alt="(.*?)".*?/>'
        reg = r'<li class="p1 m1"><a class="link-hover" href="(.*?)" title="(.*?)"><img class="lazy" data-original="(.*?)" src=".*?" alt=".*?">'
        playList = utils.parse(result, reg)
        print("playlist:", playList)
        for i in playList:
            imageUrl = self._baseUrl + i[2] 
            listitem = xbmcgui.ListItem(i[1],thumbnailImage=imageUrl)
            url = self.gen_plugin_url({"act": "detail", 
                                     "url": i[0],
                                     "title": i[1]})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        listitem = xbmcgui.ListItem("next page >> " + next_pageno,thumbnailImage=imageUrl)
        url = self.gen_plugin_url({"act": "list", 
                                 "url": self.page_url(type_id,next_pageno)})            
        xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)
        
    def movie(self):
        self.category([('全部电影',1), ('动作片',5), ('喜剧片',6), ('爱情片',7), ('科幻片',8), ('剧情片',10), ('战争片',11), ('恐怖片',9)])
    
    def tv(self):
        self.category([('全部电视剧',2), ('国产剧',12), ('欧美联盟',15), ('日韩剧场',14), ('港台剧场',13)])
            
    def search(self):
        if "keyword" not in self._params:
            kb = Keyboard('', 'Please input Movie or TV Shows name 请输入想要观看的电影或电视剧名称')
            kb.doModal()
            if not kb.isConfirmed(): return
            sstr = kb.getText()
            if not sstr: return
            self.add_search_history(sstr)
        else:
            sstr = self._params["keyword"]
        inputMovieName=urllib.quote_plus(sstr)
            
        urlSearch = self._baseUrl + '/index.php?m=vod-search-'
        urlSearch += 'wd-'+inputMovieName
        print urlSearch
        req = urllib2.Request(urlSearch, None, self._header)
        searchResponse = self._opener.open(req).read()
        #searchReg = r'<h6 class="fl"> <a href="(.*?)".*?>(.*?)</a>'
        searchReg = r'<li class="p1 m1"><a class="link-hover" href="(.*?)" title="(.*?)"><img class="lazy" data-original="(.*?)" src=".*?" alt="(.*?)">'
        searchResult = utils.parse(searchResponse, searchReg)
        
        listitem = xbmcgui.ListItem('[COLOR FFFF00FF]Search result 当前搜索: [/COLOR][COLOR FFFFFF00]('+sstr+') [/COLOR][COLOR FF00FFFF] Total 共计：'+str(len(searchResult))+'[/COLOR]【[COLOR FF00FF00]'+'Click here for new search 点此输入新搜索内容'+'[/COLOR]】')
        xbmcplugin.addDirectoryItem(self._handle, self.gen_plugin_url({"act": "search"}), listitem, True)
        for item in searchResult:
            title = item[1]
            listitem = xbmcgui.ListItem(title, thumbnailImage=self._baseUrl + item[2])
            url = self.gen_plugin_url({"act": "detail",
                                     "url": item[0],
                                     "title": title})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)

    def episodes(self):
        print self._params
        url = self._params['url']
        title = self._params['title']
        print url
        urlDetail = self._baseUrl + url
        print urlDetail
        req = urllib2.Request(urlDetail, None, self._header)
        response = self._opener.open(req).read()
        reg = r"""<li><a title='(.*?)' href='(.*?)' target="_self"><font"""
        #reg = r'<li><a href="(.*?)".*?>(.*?)</a>'
        pattern = re.compile(reg)
        result = pattern.findall(response)
        for i in range(len(result)):
            item = result[i]
            episodeTitle = title + " " + item[0]
            url = item[1]
            host_src, ep_num = self.parse_src_ep(url)
            if host_src != '1':
                continue
            listitem = xbmcgui.ListItem(episodeTitle)
            listitem.setInfo("video", {"Title": episodeTitle})
            listitem.setProperty("IsPlayable","true")
            url = self.gen_plugin_url({"act": "play",
                                     "url": url,
                                     "title": episodeTitle})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, False)
        xbmcplugin.endOfDirectory(self._handle)
        
    def parse_src_ep(self, url):
        #"vod-play-id-17700-src-3-num-4.html"
        urlReg = r'vod-play-id-\d*-src-(\d*)-num-(\d*).html'
        url_result = re.compile(urlReg).findall(url)[0]
        host_src = url_result[0]
        ep_num = url_result[1]
        return host_src, ep_num
    
    def play(self):
        url = self._params['url']
        title = self._params['title']

        host_src,ep_num = self.parse_src_ep(url)
        print(host_src, ep_num)

        urlPlay = self._baseUrl + url
        print("url to play: ", urlPlay)
        req = urllib2.Request(urlPlay, None, self._header)
        response = self._opener.open(req).read()
        #print response
        reg = r"unescape\('(.*?)'\)"
        pattern = re.compile(reg)
        result = urllib.unquote(pattern.findall(response)[0])
        sources = result.split("$$$")
        for i in range(len(sources)):
            source = sources[i]
            movie_epnum = source.split("#")[int(ep_num) - 1]
            sources[i] = movie_epnum.split("$")[1]
        print(sources)
        self.choose_and_play(sources, title)