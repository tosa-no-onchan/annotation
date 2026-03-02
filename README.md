### annotation  

  Scraping image filies from google.  

  ubuntu 22.04  
  snap firefox  
  geckodriver:/snap/bin/firefox.geckodriver  

  
  $ python3 scraper3.py  
  
#### 変更箇所  
```
class Collect_Image:
    def __init__(self):
        self.start_no=0
        self.down_load_count=900
        self.QUERY = "雑草"  <-- 適当に変更する
        ...
```
