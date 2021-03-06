# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


## Based on sample code
## https://github.com/JMSCHKU/LegcoCouncilVotes/blob/master/legcovotes/pipelines.py

from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.contrib.exporter import CsvItemExporter
import os


def item_type(item):
    return type(item).__name__.replace('Item', '').lower()  # TeamItem => team


class MultiCSVItemPipeline(object):
    """
    Save each item type in its own csv file
    """

    SaveTypes = ['moviedetails', 'movierevenue']

    save_path = os.path.join("data", "csv")

    def __init__(self):
        dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

        # create path if it does not exist
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def spider_opened(self, spider):
        self.files = dict([(name, open('data/csv/' + name + '.csv', 'w+b')) for name in self.SaveTypes])
        self.exporters = dict([(name, CsvItemExporter(self.files[name], delimiter='\t')) for name in self.SaveTypes])
        [e.start_exporting() for e in self.exporters.values()]

    def spider_closed(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        what = item_type(item)
        if what in set(self.SaveTypes):
            self.exporters[what].export_item(item)
        return item
