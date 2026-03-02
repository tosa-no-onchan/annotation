### annotation  

  Scraping image filies from google.  

  ubuntu 24.04  
  python 3.12.3  
  snap firefox  
  geckodriver:/snap/bin/firefox.geckodriver  
  $ ls /snap/bin/firefox.geckodriver  
  上記で、有無がわかる。多分あると思うので、すぐ使える。  

#### 必要パッケージ  
$ python -m pip install selenium  

#### 実行  
  $ python3 scraper3.py  
  
  ./data/{self.QUERY} に、保存される。  
  一応、今も大丈夫みたいじゃ。2026.3.2 by nishi 
  
#### 実行前に変更  
```
class Collect_Image:
    def __init__(self):
        self.start_no=0
        self.down_load_count=900
        self.QUERY = "雑草"  # <-- 適当に変更する
        self.LIMIT_DL_NUM = self.start_no + self.down_load_count

        # 出力フォルダの作成
        #project_dir = Path(__file__).resolve().parent.parent
        self.project_dir='.'
        self.save_dir = os.path.join(self.project_dir, 'data', self.QUERY)  # data <-- 保存場所
        ...
```
