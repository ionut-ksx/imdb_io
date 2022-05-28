# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Movie(scrapy.Item):
    # define the fields for your item here like:
    category = scrapy.Field()
    date_of_scraping = scrapy.Field()
    director = scrapy.Field()
    poster_img = scrapy.Field()
    raiting = scrapy.Field()
    release_year = scrapy.Field()
    title = scrapy.Field()
    top_cast = scrapy.Field()
    url = scrapy.Field()


class Actors(scrapy.Item):
    name = scrapy.Field()
    url_id = scrapy.Field()
    filmography_movies_name = scrapy.Field()


class ActorsAndMovies(scrapy.Item):
    actor_id = scrapy.Field()
    movie_url = scrapy.Field()
