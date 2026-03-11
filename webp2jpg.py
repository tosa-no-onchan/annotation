# -*- coding: utf-8 -*-
"""
webp22jpg.py

https://qiita.com/ussu_ussu_ussu/items/22f37495a47cf6a53175
"""

import os
from PIL import Image

class Web2jpg:
    def __init__(self):
        #self.base_dir="data-backup"
        self.base_dir="data"
        #self.obj="雑草"
        #self.obj="樹木"
        #self.obj="庭の鉢植えの植物"
        self.obj="草"
        # 変換元のフォルダパス
        #self.source_folder = "data-backup/"+self.obj
        self.source_folder =os.path.join(self.base_dir, self.obj)
        # 変換先のフォルダパス
        #self.destination_folder = "data-backup/"+self.obj
        self.destination_folder = os.path.join(self.base_dir,self.obj)

    def conv(self):
        # 変換元のフォルダ内のファイルを取得
        self.files = os.listdir(self.source_folder)
        # 変換元のフォルダ内のすべてのファイルについて処理
        for file in self.files:
            # ファイルの絶対パス
            file_path = os.path.join(self.source_folder, file)
            #print("file_path:",file_path)
            # webpファイルかどうかを確認
            if file.lower().endswith('.webp'):
                print("change to jpeg:",file_path)
                # webp画像を開く
                img = Image.open(file_path)
                # 変換先のファイルパスを生成 (拡張子を.jpgに変更)
                destination_path = os.path.join(self.destination_folder, os.path.splitext(file)[0] + ".jpg")
                # RGBAならRGBに変換して背景を白にする
                if img.mode == 'RGBA':
                    # 透明部分を白で塗りつぶす
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3]) # 3番目のチャンネルはアルファ
                    background.save(destination_path, 'JPEG')
                else:
                    # jpg形式で保存
                    img.convert('RGB').save(destination_path, 'JPEG')
                    #img.save(destination_path, 'JPEG')
                # 画像を閉じる
                img.close()
                os.remove(file_path)


if __name__ == '__main__':

    web2jpg = Web2jpg()
    web2jpg.conv()