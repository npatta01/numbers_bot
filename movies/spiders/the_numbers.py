# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from movies.items import MovieDetailsItem


class TheNumbersSpider(CrawlSpider):
    name = "the_numbers"
    allowed_domains = ["the-numbers.com"]
    start_urls = (
        #'http://www.the-numbers.com/',
        "http://www.the-numbers.com/movie/Jurassic-World#tab=summary"
    )

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=('movies\/year\/',)), callback='parse_movies_in_year', follow=True),
        Rule(LinkExtractor(allow=('movie\/.*#tab=summary',)), callback='parse_movie_summary'),
    )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        item = scrapy.Item()
        item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        item['name'] = response.xpath('//td[@id="item_name"]/text()').extract()
        item['description'] = response.xpath('//td[@id="item_description"]/text()').extract()
        return item

    def parse_movie_box_office(self, response):
        self.logger.info('Parsing movie box office details from  %s', response.url)

    def parse_movie_summary(self, response):
        self.logger.info('Parsing movie %s', response.url)
        financials_tab_url = response.url + '#tab=box-office'
        self.logger.info('Parsing movie %s', financials_tab_url)
        #yield scrapy.Request(financials_tab_url, callback=self.parse_movie_box_office)

        title = response.xpath("//h1[@itemprop='name']/text()").extract()

        content = response.xpath('//*[@id="summary"]')

        try:
            synopsis = content.xpath("//h2[text() ='Synopsis']/following::p[1]/text()").extract()[0]
        except :
            synopsis=''

        movie_detail_tbl = content.xpath("(//h2[text() ='Movie Details']/following::table)[1]")
        # movie_dtl_tbl


        budget = self.get_content(movie_detail_tbl, 'Budget')

        release_date = self.get_content(movie_detail_tbl, 'Releases')

        rating = self.get_content(movie_detail_tbl, 'MPAA', elem_type='a')

        running_time = self.get_content(movie_detail_tbl, 'Running Time')

        franchise = self.get_content(movie_detail_tbl, 'Franchise', elem_type='a')

        keywords = self.get_content(movie_detail_tbl, 'Keywords', elem_type='a')

        source = self.get_content(movie_detail_tbl, 'Source', elem_type='a')

        genre = self.get_content(movie_detail_tbl, 'Genre', elem_type='a')
        creative_type = self.get_content(movie_detail_tbl, 'Creative', elem_type='a')
        production_companies = self.get_content(movie_detail_tbl, 'Companies', elem_type='a')

        mdetail = MovieDetailsItem()
        mdetail['title'] = title
        mdetail['budget'] = budget
        mdetail['release_date'] = release_date
        mdetail['rating'] = rating
        mdetail['running_time'] = running_time
        mdetail['franchise'] = franchise
        mdetail['keywords'] = keywords
        mdetail['source'] = source
        mdetail['genre'] = genre
        mdetail['creative_type'] = creative_type
        mdetail['production_companies'] = production_companies
        mdetail['synopsis']=synopsis

        k = 9
        yield mdetail

    def get_content(self, selector_elem, field, elem_type=None):
        # xpath_val = "(//tr/td[b[contains(text(),'%s')]]/following::td/text())[1]" % (field)
        xpath_val = "(//tr/td[b[contains(text(),'%s')]]/following::td)[1]" % (field)

        try:
            node = selector_elem.xpath(xpath_val)
            if elem_type != None:
                node = node.xpath(elem_type)

            node=node.xpath("text()")
            val = node.extract()
            val = "::".join(val)
        except:
            val = ''

        return val

    def parse_movies_in_year(self, response):
        self.logger.info('Parsing movies in link %s', response.url)
        # yield scrapy.Request(url=response.url,callback=self.parse_movie)
