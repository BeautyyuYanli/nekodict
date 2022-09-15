import os
import argparse
import requests
from termcolor import colored as cl
from bs4 import BeautifulSoup
__version__ = '0.1.2'


def output(result):
    width = os.get_terminal_size().columns
    print('=' * width)

    # print word
    word = '[{}]'.format(result['word'])
    white = ' ' * ((width - len(word))//2)
    print(white + cl(word,
          'green', attrs=['bold', 'underline']))

    # print phonetic
    white = ' ' * ((width - len(' '.join(result['phonetic'])))//2)
    print(white + cl(' '.join(result['phonetic']), 'yellow'))

    # print explains
    print(
        cl('\n\n'.join([cl('>> ', "red") + x for x in result['explains']]), 'white'))
    print('=' * width)

    # print webexplains
    for i in result['webexplains']:
        for j in range(len(i)):
            if j == 0:
                print(cl(i[j], 'blue'))
            else:
                print(cl(i[j], 'white'))
    print()

    # print webphase
    for i in result['webphase']:
        for j in range(len(i)):
            if j == 0:
                print(cl(i[j], 'cyan'))
            else:
                print(cl(i[j], 'white'))


def process(bs: BeautifulSoup):
    result = dict({
        'word': '',
        'phonetic': [],
        'explains': [],
        'webexplains': [],
        'webphase': [],
    })

    tag_phonetic = bs.select_one('.phone_con')
    if tag_phonetic != None:
        for i in tag_phonetic.select('.per-phone'):
            result['phonetic'].append(i.text)

    tag_explains = bs.select_one('.trans-container>ul')
    if tag_explains != None:
        for i in tag_explains.select('.word-exp'):
            result['explains'].append(i.text)

    tag_webexplains = bs.select_one('.trans-list')
    if tag_webexplains != None:
        for i in tag_webexplains.select('.mcols-layout>.col2'):
            tmp = []
            for j in i.select('p'):
                if j.text != '':
                    tmp.append(j.text)
            result['webexplains'].append(tmp)

    tag_webphase = bs.select_one('.webPhrase>ul')
    if tag_webphase != None:
        for i in tag_webphase.select('.mcols-layout>.col2'):
            tmp = []
            for j in i.children:
                tmp.append(j.text)
            result['webphase'].append(tmp)

    return result


def search(session, word):
    url = 'https://www.youdao.com/result'
    params = {"word": word, "lang": "en"}
    r = session.get(url, params=params)
    if r.status_code != 200:
        raise Exception('Network error: {}'.format(r.status_code))
    bs = BeautifulSoup(r.text, 'html.parser')
    return bs


def suggest(session, word):
    url = 'https://dict.youdao.com/suggest'
    params = {'num': 1, 'ver': 3.0, 'doctype': 'json',
              'cache': 'false', 'le': 'en', 'q': word}
    r = session.get(url, params=params)
    if r.status_code != 200:
        raise Exception('Network error: {}'.format(r.status_code))
    r = r.json()
    if r['result']['code'] != 200:
        if r['result']['code'] == 404:
            return None
        else:
            raise Exception('Error from Youdao, {}: {}'.format(
                r['result']['code'], r['result']['msg']))
    return r['data']['entries'][0]['entry']


def main():
    parser = argparse.ArgumentParser(
        description='Neko Dictionary is a light-weight command line EN-ZH dictionary.')
    parser.add_argument('-v', '--version',
                        action='version', version=__version__)
    parser.add_argument('word', type=str, nargs='*')
    args = parser.parse_args()

    def routine(word):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0'
        })
        word = suggest(session, word)
        if word == None:
            print('未找到该单词')
            return
        bs = search(session, word)
        result = process(bs)
        result['word'] = word
        output(result)

    if args.word == []:
        while 1:
            word = input(cl('\n^._.^= ∫ ', 'magenta'))
            if word == '':
                continue
            elif word != 'q':
                routine(word)
            else:
                print(cl('\n/ᐠ .ᆺ. ᐟ\ﾉ Bye~', 'yellow'))
                break
    else:
        word = " ".join(args.word)
        routine(word)


if __name__ == '__main__':
    main()
