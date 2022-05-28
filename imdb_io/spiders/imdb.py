import scrapy
import re
from imdb_io.items import Movie, Actors, ActorsAndMovies
import time


class MovieSpider(scrapy.Spider):
    name = "imdb"
    allowed_domains = ["www.imdb.com"]
    start_urls = ["https://www.imdb.com/user/ur24609396/watchlist"]
    # start_urls = ["https://www.imdb.com/title/tt1194616/"]

    def extract_movie_id(self, response):
        pattern = re.compile(r"[^t]const.{3}tt\d{7}")
        movie_ids = re.findall(pattern, response.text)
        movie_ids = [x.replace('"const":"', "") for x in movie_ids]
        return movie_ids[:2]

    def extract_actor_id(self, response):
        print(response.url)
        pattern = re.compile(r"nm\d{7}")
        actor_ids = re.findall(pattern, response.text)
        # actor_ids = [x.replace('"const":"', "") for x in actor_ids]
        return actor_ids[:2]

    def parse(self, response):
        movies_id_list = self.extract_movie_id(response)
        for id_m in movies_id_list:
            url = "https://www.imdb.com/title/" + id_m + "/"
            yield scrapy.Request(url=url, callback=self.parse_movies)

    def parse_movies(self, response):
        movie = Movie()
        movie_section = response.xpath("//main/div/section[1]/section/div[3]/section")
        for item in movie_section.getall():
            movie["date_of_scraping"] = time.ctime()
            movie["title"] = response.xpath(".//h1/text()").get()
            movie["raiting"] = response.xpath(
                ".//div[@class='sc-94726ce4-0 cMYixt']//span[contains(@class, 'sc-7ab21ed2-1 jGRxWM')]/text()"
            ).get()
            movie["category"] = response.xpath(
                ".//div[@class='sc-16ede01-8 hXeKyz sc-910a7330-11 GYbFb']//li[@class='ipc-inline-list__item ipc-chip__text']/text()"
            ).getall()
            date_of_scraping = ""
            movie["director"] = response.xpath(".//div[@class='sc-fa02f843-0 fjLeDR']//ul/li/a/text()").get()
            movie["release_year"] = response.xpath(".//span[contains(@class, 'sc-8c396aa2-2 itZqyK')]/text()").get()
            movie["url"] = response.url

            top_cast = response.xpath("//main/div/section[1]/div/section/div/div[1]/section[4]/div[2]").getall()
            for item in top_cast:
                movie["top_cast"] = response.xpath(".//div[@class='sc-18baf029-7 eVsQmt']//a/text()").getall()

            yield movie

        actors_id_list = self.extract_actor_id(response)
        url_actor = "https://www.imdb.com/name/"
        for id_a in actors_id_list:
            yield scrapy.Request(url=url_actor + id_a, callback=self.parse_actors)

    def parse_actors(self, response):
        actor = Actors()
        actor["name"] = response.xpath("//h1[@class='header']/span/text()").get()
        filmography = response.xpath("//*[@id='filmography']/div[2]").getall()
        for item in filmography:
            actor["url_id"] = response.xpath("//b/a/@href").getall()
            actor["filmography_movies_name"] = response.xpath("//b/a/text()").getall()
        yield actor
