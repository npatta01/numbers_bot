# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieDetailsItem(scrapy.Item):
    """
    Details of a movie
    """

    title = scrapy.Field()
    synopsis = scrapy.Field()
    budget = scrapy.Field()
    release_date = scrapy.Field()
    rating = scrapy.Field()
    running_time = scrapy.Field()
    franchise = scrapy.Field()
    keywords = scrapy.Field()
    source = scrapy.Field()
    genre = scrapy.Field()
    creative_type = scrapy.Field()
    production_companies = scrapy.Field()



class MovieRevenueItem(scrapy.Item):
    """
    Revenue for a day in a movie's showing
    """

    title = scrapy.Field()
    date = scrapy.Field()
    rank = scrapy.Field()
    gross = scrapy.Field()
    change = scrapy.Field()
    num_theaters = scrapy.Field()
    avg_theaters_income = scrapy.Field()
    total_gross = scrapy.Field()
    days_gross = scrapy.Field()
