# -*- coding: utf-8 -*-
"""
annotaion/scraper3.py

https://qiita.com/coticoticotty/items/46b1750fd483630de1a2

"""

import os
from pathlib import Path
import random
import re
import requests
import string
import sys
import time

#import re
import cv2
import base64
import numpy as np
import io


from selenium import webdriver

# Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException


def get_out_line(text,keyword="class="):
    text=text.replace('>','>\n')
    words=text.split('\n')
    for word in words:
        print(word)


class Collect_Image:
    def __init__(self):
        self.start_no=0
        self.down_load_count=900
        self.QUERY = "雑草"
        self.LIMIT_DL_NUM = self.start_no + self.down_load_count

        # 出力フォルダの作成
        #project_dir = Path(__file__).resolve().parent.parent
        self.project_dir='.'
        self.save_dir = os.path.join(self.project_dir, 'data', self.QUERY)
        os.makedirs(self.save_dir, exist_ok=True)

        self.DRIVER_PATH = self.project_dir

        self.RETRY_NUM = 3
        self.TIMEOUT = 3

        self.file_n=self.start_no
        
        if True:
            # for Ubuntu 22.04 FireFox
            # geckodriverのパス指定
            self.executable_path="/snap/bin/firefox.geckodriver"
            options = Options()
            ### ユーザーエージェントの設定
            user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'
            options.add_argument('--user-agent=' + user_agent)

            ### ブラウザの言語設定を日本語にする
            options.set_preference("intl.accept_languages", "jpn")

            ### その他optionsの指定
            options.add_argument('--no-sandbox')  ## Sandboxの外でプロセスを動作させる
            options.add_argument('--headless')  ## ブラウザを表示しない　CLIで起動する際は必須
            options.add_argument('--disable-dev-shm-usage')  ## /dev/shmパーティションの使用を禁止し、パーティションが小さすぎることによる、クラッシュを回避する。

            ## driverの作成
            service = FirefoxService(executable_path=self.executable_path)
            self.driver = webdriver.Firefox(options=options,service=service)

        else:
            # for Chrome
            # フルスクリーンにする
            options = webdriver.ChromeOptions()
            options.add_argument("--start-fullscreen")
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')  # headlessモードで暫定的に必要なフラグ(そのうち不要になる)
            options.add_argument('--disable-extensions')  # すべての拡張機能を無効にする。ユーザースクリプトも無効にする
            options.add_argument('--proxy-server="direct://"')  # Proxy経由ではなく直接接続する
            options.add_argument('--proxy-bypass-list=*')  # すべてのホスト名
            options.add_argument('--start-maximized')  # 起動時にウィンドウを最大化する


            self.driver = webdriver.Chrome(self.DRIVER_PATH, options=options)

    """
     表示されるサムネイル画像をすべて取得する
    """
    def collect_images(self):

        #project_dir = Path(__file__).resolve().parent.parent

        # 指定したURLに移動
        url = f'https://www.google.com/search?q={self.QUERY}&tbm=isch'

        # タイムアウト設定
        self.driver.implicitly_wait(self.TIMEOUT)

        # グーグルの画像検索を行う。
        self.driver.get(url)

        if False:
            html=driver.page_source
            #print('driver.page_source:',driver.page_source)
            f = open('google_search.html', 'w')
            f.write(html)
            f.close()

            #sys.exit()
        
        #----------------------------------------------
        # gooble 検索の本体ページ で使われている class name
        #  将来変わったら、自分で変更してください。
        #------------------------------------------------
        # class="YQ4gaf zr758c Q4LuWd"
        # ページroll down 用
        class_name='czzyk'

        # 本体画面のサムイル画像 用
        # クリックして、右プレビュー画面に表示する処理で使用。
        class_name_thumb='ob5Hkd'       # <h3 class="ob5Hkd" -> この中に <a タグがある
                                        #  <a ...
        # 右プレビュー画面 の画像の特定用に使用。
        #class_name_thumb2='YsLeY'      # 右のプレビューページ <a class="YsLeY"
                                        # 画像は、2 有る
        #class_name_thumb2='sFlh5c'      # 右のプレビューページ img1 <img class="sFlh5c iPVvYb"
        class_name_thumb2='iPVvYb'      # 右のプレビューページ img1 <img class="sFlh5c iPVvYb"

        thumbnail_elements = self.driver.find_elements(By.CLASS_NAME, class_name)

        # 取得したサムネイル画像数を数える
        count = len(thumbnail_elements)
        print("count:",count)

        loop_cnt=0
        prev_count=count
        # 画面のスクロールをします。
        # 取得したい枚数以上になるまでスクロールする
        while loop_cnt < 50 and count < self.LIMIT_DL_NUM:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)

            # サムネイル画像の取得
            # multiple
            thumbnail_elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            # 一個
            # element = driver.find_element(by=By.ID, value='id')
            count = len(thumbnail_elements)
            print("count:",count)
            if count <= 0 or prev_count == count:
                break
            prev_count=count
            loop_cnt += 1

        # HTTPヘッダーの作成
        HTTP_HEADERS = {'User-Agent': self.driver.execute_script('return navigator.userAgent;')}
        print(HTTP_HEADERS)

        # 画像をダウンロードするためのURLを格納
        image_urls = []
        image_urls_ext=[]

        # 本体の contentの、サムネイルをクリックしたときに、右に現れる、プレビュー表示の画像をクリックして、
        #  画像のURLを取得してダウンロードする。
        # エラーの処理は苦し紛れ
        # うまく取得できるまで、最大3回はトライする
        thumbnail_elements=thumbnail_elements[self.start_no:]
        for index, thumbnail_element in enumerate(thumbnail_elements):
            is_clicked = False
            
            print('passed:#5')
            #print(thumbnail_element.get_attribute('href'))
            #print(thumbnail_element.get_attribute('innerHTML'))

            for i in range(self.RETRY_NUM):
                # メイン Contentのサムネイル一覧の、サムネイルを、Browser engine からクリックする。
                # 場合によっては失敗するのでtry-exceptでエラー処理
                try:
                    if is_clicked == False:
                        image_element = thumbnail_element.find_element(By.CLASS_NAME, class_name_thumb)
                        image_url = image_element.find_element(By.TAG_NAME,'a')
                        thumbnail_element.click()
                        time.sleep(2)
                        is_clicked = True
                except NoSuchElementException:
                    print(f'****NoSuchElementException*****')
                    continue
                except Exception:
                    print('予期せぬエラーです')
                    break

                print('passed:#6')
                try:
                    # 右のプレビュー更新されれば、画像の URL の class_name_thumb2 が取得できるはず
                    #current_html = self.driver.page_source
                    #print('current_html:',current_html)
                    #get_out_line(current_html)
                    #sys.exit(0)
                    image_element = self.driver.find_element(By.CLASS_NAME, class_name_thumb2)
                    image_url = image_element.get_attribute('src')

                    #print('image_url:',image_url)
                    if re.match(r'data:image', image_url):
                        print(f'URLが変わるまで待ちましょう。{i+1}回目')
                        time.sleep(2)
                        if i+1 == self.RETRY_NUM:
                            print(f'urlは変わりませんでしたね。。。')
                        continue
                    else:
                        # 画像の URL が取れたようなので、大きい画像のimgタグの src から画像を取得
                        #print(f'image_url: {image_url}')
                        #image_urls.append(image_url)
                        self.down_load_image_ext(image_url, self.save_dir, 3, HTTP_HEADERS)
                        break

                except NoSuchElementException:
                    print(f'****NoSuchElementException*****')
                    break

                except ElementClickInterceptedException:
                    print(f'***** click エラー: {i+1}回目')
                    self.driver.execute_script('arguments[0].scrollIntoView(true);', thumbnail_element)
                    time.sleep(1)
                else:
                    break

            #print('index:',index)
            if (index+self.start_no+1) % 20 == 0:
                print('>>>',f'{index+self.start_no+1}件完了')
            time.sleep(1)

        for image_url in image_urls:
            self.down_load_image_ext(image_url, self.save_dir, 3, HTTP_HEADERS)

        for image_url in image_urls_ext:
            self.down_load_image_ext(image_url, self.save_dir, 3, HTTP_HEADERS)
            #sys.exit(0)

        self.driver.quit()

    def get_extension(self,url):
        url_lower = url.lower()
        extension = re.search(r'\.jpg|\.jpeg|\.png', url_lower)
        if extension:
            return extension.group()
        else:
            return None

    def randomname(self,n):
        randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
        return ''.join(randlst)

    def down_load_image(self,url, save_dir, loop, http_header):
        result = False
        for i in range(loop):
            try:
                r = requests.get(url, headers=http_header, stream=True, timeout=10)
                r.raise_for_status()

                extension = self.get_extension(url)
                file_name = self.randomname(12)
                file_path = save_dir + '/' + file_name + extension

                with open(file_path, 'wb') as f:
                    f.write(r.content)

                print(f'{url}の保存に成功')

            except requests.exceptions.SSLError:
                print('*****SSLエラー*****')
                break

            except requests.exceptions.RequestException as e:
                print(f'***** requests エラー ({e}): {i+1} 回目')
                time.sleep(1)
            else:
                result = True
                break
        return result


    # https://qiita.com/donksite/items/21852b2baa94c94ffcbe
    def down_load_image_ext(self,url, save_dir, loop, http_header):
        result = False
        #print('down_load_image_ext() url:',url)
        for i in range(loop):
            try:
                r = requests.get(url, headers=http_header, stream=True, timeout=10)
                r.raise_for_status()
                content_type=r.headers["content-type"]
                print('content_type:',content_type)
                if not content_type.startswith('image/'):
                    return

                extension=content_type.split('/')[-1]
                self.file_n +=1

                file_path = save_dir + '/' + f"{self.file_n}."+extension
                with open(file_path, 'wb') as f:
                    f.write(r.content)

                print(f'{url}の保存に成功')

            except requests.exceptions.SSLError:
                print('*****SSLエラー*****')
                break

            except requests.exceptions.RequestException as e:
                print(f'***** requests エラー ({e}): {i+1} 回目')
                time.sleep(1)
            else:
                result = True
                break
        return result


if __name__ == '__main__':
    collect_images=Collect_Image()
    collect_images.collect_images()

