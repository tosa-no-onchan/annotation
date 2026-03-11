'''
resize2dtr_size.py

huggin face DTR の、ディフォルト input size=(480,480) にリサイズします。
画像サイズを、480x480 にアスペクト比を維持して、リサイズします。
余白は、黒で埋めます。

リサイズした後、 labelImg で、アノテーションをしたほうが、実際の画像サイズがわかるので、
あまり小さい、 Target は、使わないほうが良い!!

'''

import cv2
import numpy as np
import os

'''
hugging face DTR の学習には、480x480 にアスペクトを維持して、余白を、黒にした画像を
使います。
  padding=True
    画像サイズを、 480x480 にして、余白を埋める。
  padding=False
    アスペクト比を維持して、どちらかが、 480 になるように縮小します。
    画像の余白は、出ません。
'''
def preprocess_universal(image_path, target_size=480,padding=False):
    # 1. 画像読み込み (BGR -> RGB)
    img = cv2.imread(image_path)
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # BGR -> RGB
    h, w = img.shape[:2]

    # 2. アスペクト比維持のリサイズ (LongestMaxSize相当)
    scale = target_size / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    if not padding:
      return resized
     
    # 3. パディング (PadIfNeeded / Center相当)
    pad_h = (target_size - new_h) // 2
    pad_w = (target_size - new_w) // 2
    # 上下左右に黒帯を追加
    padded = cv2.copyMakeBorder(
        resized, pad_h, target_size - new_h - pad_h,
        pad_w, target_size - new_w - pad_w,
        cv2.BORDER_CONSTANT, value=(0, 0, 0)
    )
       
    #print('type(padded):',type(padded))
    # こちらは、 rknn への、入力時用です。今回は、使わない!!
    if False:
      # 4. 正規化 (DETR標準: Mean=[0.485, 0.456, 0.406], Std=[0.229, 0.224, 0.225])
      # ※RKNN変換時にモデルに組み込むことも可能ですが、手動なら以下
      input_data = padded.astype(np.float32) / 255.0
      mean = np.array([0.485, 0.456, 0.406])
      std = np.array([0.229, 0.224, 0.225])
      input_data = (input_data - mean) / std

      # 5. HWC -> CHW 変換 (ONNX/RKNN用)
      input_data = input_data.transpose(2, 0, 1)
      input_data = np.expand_dims(input_data, axis=0) # バッチ次元追加

      return input_data, (h, w), (pad_h, pad_w), scale
    else:
       return padded

class ResizeImg:
    def __init__(self):
      self.target_size=480
      self.padding=False    # hugging face DTR の学習用は、True が、お勧め!!
      self.source_dir="data"
      self.dist_dir="data-backup"
      
      #self.obj="雑草"
      #self.obj="樹木"
      self.obj="庭の鉢植えの植物"
      #self.obj="草"
      # 変換元のフォルダパス
      #self.source_folder = "data-backup/"+self.obj
      self.source_folder =os.path.join(self.source_dir, self.obj)
      self.dist_folder =os.path.join(self.dist_dir, self.obj)

      # フォルダを作成（存在する場合は無視する）
      os.makedirs(self.dist_folder, exist_ok=True)

    def __call__(self):
        # 変換元のフォルダ内のファイルを取得
        self.files = os.listdir(self.source_folder)
        # 変換元のフォルダ内のすべてのファイルについて処理
        for file in self.files:
            file_path = os.path.join(self.source_folder, file)
            save_path = os.path.join(self.dist_folder, file)
            print("file_path:",file_path)
            print("save_path:",save_path)
            img=preprocess_universal(file_path,target_size=self.target_size,padding=self.padding)
            if False:
              cv2.imshow("Result", img)
              key =cv2.waitKey()
            # 画像を保存する
            cv2.imwrite(save_path, img)


if __name__ == '__main__':
  resizeImg=ResizeImg()
  resizeImg()
