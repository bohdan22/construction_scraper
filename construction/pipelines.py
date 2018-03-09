import pymongo
from datetime import timedelta

from scrapy import signals
from scrapy.exporters import JsonItemExporter


class MongoDBPipeline(object):
    collection_name = 'profiles'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item


class StatsPipeline(object):
    def __init__(self, stats):
        self.file = open('stats.txt', 'a')
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.stats)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def spider_closed(self, spider):
        delta = self.stats.get_value('finish_time') - self.stats.get_value('start_time')
        self.file.write(str({
            'start_datetime': self.stats.get_value('start_time'),
            'finish_datetime': self.stats.get_value('finish_time'),
            'total_time_spent': '{}'.format(timedelta(seconds=delta.seconds)),
            'profiles_added': self.stats.get_value('item_scraped_count'),
            'profiles_total': self.stats.get_value('item_scraped_count'),
            'errors_count': self.stats.get_value('log_count/ERROR'),
            'retries_count': self.stats.get_value('retry/count')
        }))
        self.file.close()


class ProfilePipeline(object):
    def __init__(self):
        self.file = open("profiles.json", 'ab')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):

        self.exporter.export_item(item)
        return item