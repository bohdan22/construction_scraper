from datetime import timedelta

import pymongo
from scrapy import signals

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log


class MongoDBPipeline(object):

    def __init__(self, stats):
        # logs info
        self.stats = stats
        # Mongodb
        connection = pymongo.MongoClient(settings['MONGODB_HOST'], settings['MONGODB_PORT'])
        db = connection[settings['MONGODB_DATABASE']]
        self.profiles_collection = db[settings['MONGODB_PROFILES_COLLECTION']]
        self.logs_collection = db[settings['MONGODB_LOGS_COLLECTION']]

        self.added = 0

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.stats)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def spider_closed(self, spider):
        delta = self.stats.get_value('finish_time') - self.stats.get_value('start_time')
        self.logs_collection.insert_one({
            'start_datetime': self.stats.get_value('start_time'),
            'finish_datetime': self.stats.get_value('finish_time'),
            'total_time_spent': '{}'.format(timedelta(seconds=delta.seconds)),
            'profiles_added': self.added,
            'profiles_total': self.profiles_collection.count(),
            'errors_count': self.stats.get_value('log_count/ERROR'),
            'retries_count': self.stats.get_value('retry/count')
        })

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid and not self.profiles_collection.find_one({'profile_url': item['profile_url']}):
            self.profiles_collection.insert_one(dict(item))
            self.added += 1
            log.msg("------------>>>>>>Profile added to MongoDB database!<<<<<<<------------",
                    level=log.DEBUG, spider=spider)
        return item