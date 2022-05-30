# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Test(scrapy.Item):
    url = scrapy.Field()


class Movie(scrapy.Item):
    # define the fields for your item here like:
    category = scrapy.Field()
    date_of_scraping = scrapy.Field()
    director = scrapy.Field()
    rating = scrapy.Field()
    release_year = scrapy.Field()
    title = scrapy.Field()
    top_cast = scrapy.Field()
    url = scrapy.Field()
    # poster_img = scrapy.Field()


class Actor(scrapy.Item):
    filmography_movie_name = scrapy.Field()
    name = scrapy.Field()
    url_id = scrapy.Field()


class MovieActors(scrapy.Item):
    actor_url = scrapy.Field()
    movie_url = scrapy.Field()
