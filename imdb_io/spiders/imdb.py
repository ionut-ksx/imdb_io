import scrapy
import re
from imdb_io.items import Movie, Actor, MovieActors
import time
import ipdb


class MovieSpider(scrapy.Spider):
    name = "imdb"
    allowed_domains = ["www.imdb.com", "m.media-amazon.com"]
    start_urls = ["https://www.imdb.com/user/ur24609396/watchlist"]

    def extract_movie_id(self, response):
        pattern = re.compile(r"[^t]const.{3}tt\d{7}")
        movie_ids = re.findall(pattern, response.text)
        movie_ids = [x.replace('"const":"', "") for x in movie_ids]
        return movie_ids

    def extract_actor_id(self, response):

        """returns 18 title ids"""
        # pattern = re.compile(r"nm\d{7}")
        # actor_ids = re.findall(pattern, response.text)
        actor_ids = response.xpath("//div/a[@data-testid='title-cast-item__actor']").re(r"nm\d{7}")
        return actor_ids

    def parse(self, response):
        movies_id_list = self.extract_movie_id(response)
        for id_m in movies_id_list:
            url = "https://www.imdb.com/title/" + id_m + "/"
            yield scrapy.Request(url=url, callback=self.parse_movie)

    def parse_movie(self, response):
        movie = Movie()
        # movie_section = response.xpath("//main/div/section[1]/section/div[3]/section")
        movie["date_of_scraping"] = time.ctime()
        movie["url"] = response.url
        movie["image_urls"] = [
            response.xpath(
                "//div[contains(@class, 'ipc-media ipc-media--poster-27x40 ipc-image-media-ratio--poster-27x40')]/img[@class='ipc-image']/@src"
            ).get()
        ]
        # for item in movie_section.getall():
        movie["title"] = response.xpath(".//h1/text()").get()
        movie["rating"] = response.xpath(
            ".//div[@class='sc-94726ce4-0 cMYixt']//span[contains(@class, 'sc-7ab21ed2-1 jGRxWM')]/text()"
        ).get()
        movie["category"] = str(
            response.xpath("//ul/li[@class='ipc-inline-list__item ipc-chip__text']/text()").getall()
        )
        movie["director"] = response.xpath(".//div[@class='sc-fa02f843-0 fjLeDR']//ul/li/a/text()").get()
        movie["release_year"] = response.xpath(".//span[contains(@class, 'sc-8c396aa2-2 itZqyK')]/text()").get()

        # top_cast = response.xpath("//main/div/section[1]/div/section/div/div[1]/section[4]/div[2]").getall()
        # for item in top_cast:
        movie["top_cast"] = response.xpath(".//div[@class='sc-18baf029-7 eVsQmt']//a/text()").getall()
        # ipdb.set_trace()
        yield movie

        # get the actor ids
        actors_id_list = self.extract_actor_id(response)

        url_actor = "https://www.imdb.com/name/"
        meta = {"title": movie["title"]}

        for id_a in actors_id_list:
            yield scrapy.Request(url=url_actor + id_a, callback=self.parse_actor, meta=meta)
            actor_movie = MovieActors()
            actor_movie["movie_url"] = movie["url"]
            actor_movie["actor_url"] = "https://www.imdb.com/name/" + id_a
            yield actor_movie

    def parse_actor(self, response):
        actor = Actor()
        actor["name"] = response.xpath("//h1[@class='header']/span/text()").get()
        actor["url_id"] = [
            self.start_urls[0][:20] + uri for uri in response.xpath("//*[@id='filmography']//b/a/@href").getall()
        ]
        actor["filmography_movie_name"] = response.xpath("//*[@id='filmography']//b/a/text()").getall()
        yield actor
