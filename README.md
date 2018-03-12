# construction_scraper

It's a scraper that collect profiles from http://www.construction.co.uk/construction_directory.aspx

For use it you need Python 3 with installed packages(you can find them in file requirements.txt):
- Scrapy
- pymongo
- scrapy_fake_useragent

For install packages:
- pip install -r requirements.txt

Command for run spider: 
- scrapy crawl construction_spider

If you want to connect your mongo database, configure settings.py file with your mongo database settings





