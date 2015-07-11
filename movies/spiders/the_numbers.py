# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from movies.items import MovieDetailsItem, MovieRevenueItem
import urlparse


class TheNumbersSpider(scrapy.Spider):
    name = "numbers"
    allowed_domains = ["the-numbers.com"]
    # start_urls = (
    #   'http://www.the-numbers.com/',
    #    "http://www.the-numbers.com/movie/Jurassic-World#tab=summary"
    # )
    # start_urls = ["http://www.the-numbers.com/movie/Jurassic-World#tab=summary"]

    # start_urls= ["http://www.the-numbers.com/movies/year/2015"]

    # rules = (
    # Extract links matching 'category.php' (but not matching 'subsection.php')
    # and follow links from them (since no callback means follow=True by default).

    # Extract links matching 'item.php' and parse them with the spider's method parse_item
    #    Rule(LinkExtractor(allow=('movies\/year\/',)), callback='parse_movies_in_year', follow=True),
    # Rule(LinkExtractor(allow=('movie\/.*#tab=summary',)), callback='parse_movie_summary'),
    # )



    def start_requests(self):
        # yield scrapy.Request("http://www.the-numbers.com/movies/year/2014", self.parse_movies_in_year)
        # yield scrapy.Request("http://www.the-numbers.com/movie/Terminator-Genisys#tab=summary", self.parse_movie_summary)

        min_year = 2000
        max_year = 2015

        for year in range(min_year, max_year + 1):
            yield scrapy.Request("http://www.the-numbers.com/movies/year/%s" % (year), self.parse_movies_in_year)

    def parse_movie_box_office(self, response, movie_title):
        self.logger.info('Parsing movie box office details from  %s', response.url)

        daily_tbl = response.xpath("(//*[@id='box_office_chart'])[1]")

        dates_col = self.__budget_column_helper(daily_tbl, 1, is_a=True)

        rank_col = self.__budget_column_helper(daily_tbl, 2)

        gross_col = self.__budget_column_helper(daily_tbl, 3)

        change_col = self.__budget_column_helper(daily_tbl, 4)

        num_theaters_col = self.__budget_column_helper(daily_tbl, 5)

        avg_theaters_income_col = self.__budget_column_helper(daily_tbl, 6)

        total_gross_col = self.__budget_column_helper(daily_tbl, 7)

        days_gross_col = self.__budget_column_helper(daily_tbl, 8)

        movie_revenues = []
        for i in range(len(dates_col)):
            mdi = MovieRevenueItem()
            mdi['title'] = movie_title
            mdi['date'] = dates_col[i]
            mdi['rank'] = rank_col[i]
            mdi['gross'] = gross_col[i]
            mdi['change'] = change_col[i]
            mdi['num_theaters'] = num_theaters_col[i]
            mdi['avg_theaters_income'] = avg_theaters_income_col[i]
            mdi['total_gross'] = total_gross_col[i]
            mdi['days_gross'] = days_gross_col[i]

            movie_revenues.append(mdi)
        return movie_revenues

    def __budget_column_helper(self, selector_elem, idx, is_a=False):

        xpath_query = "table//td[%i]/text()" % (idx)

        if is_a:
            xpath_query = "table//td[%i]/a/text()" % (idx)

        vals = selector_elem.xpath(xpath_query).extract()
        vals = [val.replace(u'\xa0', u'') for val in vals]
        return vals

    def parse_movie_summary(self, response):
        self.logger.debug('Parsing movie %s', response.url)
        # financials_tab_url = response.url + '#tab=box-office'
        # self.logger.info('Parsing movie %s', financials_tab_url)
        # yield scrapy.Request(financials_tab_url, callback=self.parse_movie_box_office)

        title = response.xpath("//h1[@itemprop='name']/text()").extract()[0]

        content = response.xpath('//*[@id="summary"]')

        try:
            synopsis = content.xpath("//h2[text() ='Synopsis']/following::p[1]/text()").extract()[0]
        except:
            synopsis = ''

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
        mdetail['synopsis'] = synopsis

        yield mdetail

        movie_revenues = self.parse_movie_box_office(response, title)

        for item in movie_revenues:
            yield item

    # def parse_movie_response(self,response):
    #     self.logger.info('Parsing movie box info%s', response.url)
    #     financials_tab_url = response.url + '#tab=box-office'
    #     self.logger.info('Parsing movie %s', financials_tab_url)
    #     # yield scrapy.Request(financials_tab_url, callback=self.parse_movie_box_office)
    #
    #     title = response.xpath("//h1[@itemprop='name']/text()").extract()
    #
    #     content = response.xpath('//*[@id="summary"]')
    #
    #     try:
    #         synopsis = content.xpath("//h2[text() ='Synopsis']/following::p[1]/text()").extract()[0]
    #     except:
    #         synopsis = ''
    #
    #     movie_detail_tbl = content.xpath("(//h2[text() ='Movie Details']/following::table)[1]")
    #     # movie_dtl_tbl
    #     yield mdetail


    def get_content(self, selector_elem, field, elem_type=None):
        # xpath_val = "(//tr/td[b[contains(text(),'%s')]]/following::td/text())[1]" % (field)
        xpath_val = "(//tr/td[b[contains(text(),'%s')]]/following::td)[1]" % (field)

        try:
            node = selector_elem.xpath(xpath_val)
            if elem_type != None:
                node = node.xpath(elem_type)

            node = node.xpath("text()")
            val = node.extract()
            val = "::".join(val)
        except:
            val = ''

        return val

    def parse_movies_in_year(self, response):
        self.logger.info('Parsing movies in link %s', response.url)

        # all_movie_links = response.xpath("//table//a[starts-with(@href,'/movie')]/@href").extract()

        all_movie_links = response.xpath("//table/tr/td[2]//a/@href").extract()

        self.logger.info('There are %s movies in %s', (len(all_movie_links), response.url))
        for link in all_movie_links:
            single_movie_link = urlparse.urljoin(response.url, link)
            yield scrapy.Request(url=single_movie_link, callback=self.parse_movie_summary)
