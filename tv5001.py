# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2025/3/23 21:55
import base64
import sys
import time
import json
import requests
sys.path.append('..')
from base.spider import Spider
from bs4 import BeautifulSoup
import re
from datetime import datetime
from tv5001 import get_matches, get_html, extract_live_signals

class Spider(Spider):
    def getName(self):
        return "Litv"

    def init(self, extend):
        self.extend = extend
        try:
            self.extendDict = json.loads(extend)
        except:
            self.extendDict = {}

        proxy = self.extendDict.get('proxy', None)
        if proxy is None:
            self.is_proxy = False
        else:
            self.proxy = proxy
            self.is_proxy = True
        pass

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def natural_sort_key(self, s):
        """
        自然排序辅助函数
        """
        return [
            int(part) if part.isdigit() else part.lower()
            for part in re.split(r'(\d+)', s)
        ]

    def liveContent(self, url):
        live_channels = []
        s_channels = []
        base_url = "https://www.515001.tv/"
        matches = get_matches(base_url)
        print(matches)
        for match in matches:
            status = match["status"]
            name = f"[{match["name"]}]{match["home_team"]} VS {match["away_team"]} {match["time"]}"
            play_url = match["url"]
            api_url = play_url.replace("bofang","live")
            if status == "直播中":
                html = get_html(api_url)
                results = extract_live_signals(html)
                if results:
                    print("results:",results)
                    for sig in results:
                        sig_url = f"video://{sig['decoded']}"
                        sig_name = sig['name']
                        live_channels.append(f"{name}[{sig_name}],{sig_url}")
                else:
                    live_channels.append(f"{name},video://{play_url}")
            else:
                s_channels.append(f"{name},video://{play_url}")
  

        m3u_content = ['#EXTM3U']
        if live_channels:
            for i in live_channels:
                title = i.split(",")[0]
                ch_url = i.split(",")[1]
                extinf = f'#EXTINF:-1 tvg-name="{title}" group-title="515001",{title}'
                m3u_content.extend([extinf, ch_url])
        if s_channels:
            for i in s_channels:
                title = i.split(",")[0]
                ch_url = i.split(",")[1]
                extinf = f'#EXTINF:-1 tvg-name="{title}" group-title="515001",{title}'
                m3u_content.extend([extinf, ch_url])
 
        return '\n'.join(m3u_content)       

    def homeContent(self, filter):
        return {}

    def homeVideoContent(self):
        return {}

    def categoryContent(self, cid, page, filter, ext):
        return {}

    def detailContent(self, did):
        return {}

    def searchContent(self, key, quick, page='1'):
        return {}

    def searchContentPage(self, keywords, quick, page):
        return {}

    def playerContent(self, flag, pid, vipFlags):
        return {}

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        if params['type'] == "ts":
            return self.get_ts(params)
        return [302, "text/plain", None, {'Location': 'https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/mp4/xgplayer-demo-720p.mp4'}]
    def proxyM3u8(self, params):
        pid = params['pid']
        info = pid.split(',')
        a = info[0]
        b = info[1]
        c = info[2]
        timestamp = int(time.time() / 4 - 355017625)
        t = timestamp * 4
        m3u8_text = f'#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:4\n#EXT-X-MEDIA-SEQUENCE:{timestamp}\n'
        for i in range(10):
            url = f'https://ntd-tgc.cdn.hinet.net/live/pool/{a}/litv-pc/{a}-avc1_6000000={b}-mp4a_134000_zho={c}-begin={t}0000000-dur=40000000-seq={timestamp}.ts'
            if self.is_proxy:
                url = f'http://127.0.0.1:9978/proxy?do=py&type=ts&url={self.b64encode(url)}'

            m3u8_text += f'#EXTINF:4,\n{url}\n'
            timestamp += 1
            t += 4
        return [200, "application/vnd.apple.mpegurl", m3u8_text]

    def get_ts(self, params):
        url = self.b64decode(params['url'])
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, stream=True, proxies=self.proxy)
        return [206, "application/octet-stream", response.content]

    def destroy(self):
        return '正在Destroy'

    def b64encode(self, data):
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')

    def b64decode(self, data):
        return base64.b64decode(data.encode('utf-8')).decode('utf-8')


if __name__ == '__main__':
    pass
