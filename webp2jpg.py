# -*- coding: utf-8 -*-
"""
webp22jpg.py

https://qiita.com/ussu_ussu_ussu/items/22f37495a47cf6a53175
"""

import os
from PIL import Image

class Web2jpg:
    def __init__(self):
        # 変換元のフォルダパス
        self.source_folder = "data-backup/雑草"
        # 変換先のフォルダパス
        self.destination_folder = "data-backup/雑草"

    def conv(self):
        # 変換元のフォルダ内のファイルを取得
        self.files = os.listdir(self.source_folder)
        # 変換元のフォルダ内のすべてのファイルについて処理
        for file in self.files:
            # ファイルの絶対パス
            file_path = os.path.join(self.source_folder, file)
            # webpファイルかどうかを確認
            if file.lower().endswith('.webp'):
                # webp画像を開く
                img = Image.open(file_path)
                # 変換先のファイルパスを生成 (拡張子を.jpgに変更)
                destination_path = os.path.join(self.destination_folder, os.path.splitext(file)[0] + ".jpg")
                # jpg形式で保存
                img.save(destination_path, 'JPEG')
                # 画像を閉じる
                img.close()


if __name__ == '__main__':

    web2jpg = Web2jpg()
    web2jpg.conv()