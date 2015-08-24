#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Xiaodong Qi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import telegram
import requests
from bs4 import BeautifulSoup
import random
import re
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)


E_HENTAI_SEARCH_URL = 'http://g.e-hentai.org/'  # Use E-Hentai gallery. No potential child porn allowed
E_HENTAI_API_URL = 'http://g.e-hentai.org/api.php'
E_HENTAI_BOT = bot = telegram.Bot(token='TOKEN')  # TODO: Put your token here
E_HENTAI_UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'}
E_HENTAI_ARGS = {
    'f_apply': 'Apply Filter',
    'f_artistcg': 0,
    'f_asianporn': 0,
    'f_cosplay': 0,
    'f_doujinshi': 1,
    'f_gamecg': 0,
    'f_imageset': 0,
    'f_manga': 0,
    'f_misc': 0,
    'f_non-h': 0,
    'f_search': 'language:chinese %s',
    'f_western': 0
}


def get_url_from_keyword(content): # TODO: what if no hons found or IP is blocked
    args = E_HENTAI_ARGS.copy()
    args['f_search'] %= content
    eh_request = requests.get(E_HENTAI_SEARCH_URL, params=args, headers=E_HENTAI_UA)
    eh_content = eh_request.text
    eh_soup = BeautifulSoup(eh_content)
    eh_hons = eh_soup.select('div.it5 a')
    try:
        random_hon = eh_hons[random.randint(0, len(eh_hons))]
        return random_hon['href']
    except IndexError:
        return None


def get_metadata_from_url(url):
    request_data = {'method': 'gdata', 'gidlist': []}
    gid = re.findall(r'/(\d+)/([0-9a-f]+)/', url)
    request_data['gidlist'].append([int(gid[0][0]), gid[0][1]])
    api_request = requests.post(E_HENTAI_API_URL, json=request_data)
    metadata = api_request.json()['gmetadata'][0]
    return metadata['title'], metadata['thumb']


def reply(update):
    message_content = update.message.text
    search_keyword = re.findall(r'/eh (.*)', message_content)
    if not search_keyword:
        search_keyword = ''
    url = get_url_from_keyword(search_keyword)
    if url:
        meta = get_metadata_from_url(url)
        reply_content = '客官，这是你要的本子：\n' \
                        '%s\n' \
                        'URL: %s' % (meta[0], url)
        E_HENTAI_BOT.sendPhoto(chat_id=update.message.chat_id, photo=meta[1], caption=reply_content)
    else:
        E_HENTAI_BOT.sendMessage(chat_id=update.message.chat_id, text='发生了错误：\n可能是没找到本子\n或者触发了访问限制')


def main():
    offset = E_HENTAI_BOT.getUpdates(None)[-1].update_id + 1
    while True:
        updates = E_HENTAI_BOT.getUpdates(offset)
        try:
            offset = updates[-1].update_id + 1
        except IndexError:
            offset = None
        for update in updates:
            logging.log(logging.WARNING, update.message.text)
            reply(update)
        time.sleep(2)


if __name__ == '__main__':
    main()
