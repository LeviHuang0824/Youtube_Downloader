#
# Get videos url
#

from bs4 import BeautifulSoup
from requests_html import HTMLSession

Ytd_base_url = "https://www.youtube.com/"


def playlist_urls(url):
    urls = []
    if "list=" not in url:  # 如果list= 不在網址裡面，代表為單一影片
        return url
    session = HTMLSession()
    response = session.get(url)
    response.html.render(sleep=1)
    res = response.html
    bs = BeautifulSoup(res.html, "lxml")
    a_list = bs.find_all("a", {"class": "yt-simple-endpoint style-scope ytd-playlist-panel-video-renderer"})
    for i in a_list:
        href = i.get("href")
        play_list_url = f"{Ytd_base_url}{href}"
        urls.append(play_list_url)
        return urls



