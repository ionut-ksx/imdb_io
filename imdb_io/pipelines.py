# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from imdb_io.items import Movie, Actor, MovieActors
import sqlite3
import ipdb


class ImdbIoPipeline:
    def process_item(self, item, spider):
        return item


class SqlitePipeline:
    def open_spider(self, spider):

        # Create/connect to db
        self.con = sqlite3.connect("/Users/bws/BWS/Python/imdb-crawler/imdb_io/imdb_io/imdb.db")

        # Create cursor
        self.cur = self.con.cursor()

        self.create_actors_table()
        self.create_movies_table()
        self.create_movie_actors_table()

    def create_movies_table(self):
        # Drop MOVIES if exists
        self.cur.execute("""DROP TABLE IF EXISTS movies""")

        # Create MOVIES table if none exists
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS movies(
            category TEXT,
            date_of_scraping TEXT,
            director TEXT,
            rating TEXT,
            release_year TEXT,
            title TEXT,
            top_cast TEXT,
            url TEXT)
        """
        )

    def create_actors_table(self):

        # drop actors table if exists
        self.cur.execute("""DROP TABLE IF EXISTS actors""")

        # Create ACTORS table if not exists
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS actors(
            filmography_movie_name TEXT,
            name TEXT,
            url_id TEXT PRIMARY KEY
            )
        """
        )

    def create_movie_actors_table(self):
        # Drop MOVIE_ACTORS if exists
        self.cur.execute("""DROP TABLE IF EXISTS movie_actors""")

        # Create MOVIE_ACTORS table if none exists
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS movie_actors(
            record_id INTEGER PRIMARY KEY,
            actor_url TEXT,
            movie_url TEXT
            )
        """
        )

    def process_item(self, item, spider):

        if isinstance(item, Movie):
            self.cur.executemany(
                """INSERT INTO movies (category,date_of_scraping,director,rating,release_year,title,top_cast,url) VALUES (?,?,?,?,?,?,?,?)""",
                [
                    (
                        item["category"],
                        item["date_of_scraping"],
                        item["director"],
                        item["rating"],
                        item["release_year"],
                        item["title"],
                        item["top_cast"][0],
                        item["url"],
                    )
                ],
            )
        self.con.commit()

        if isinstance(item, Actor):
            self.cur.executemany(
                """INSERT INTO actors (filmography_movie_name,name,url_id) VALUES (?,?,?)""",
                [(item["filmography_movie_name"][0], item["name"], item["url_id"][0])],
            )
        self.con.commit()

        if isinstance(item, MovieActors):
            self.cur.executemany(
                """INSERT INTO movie_actors (movie_url, actor_url) VALUES (?,?)""",
                [(item["movie_url"], item["actor_url"])],
            )
        self.con.commit()


"""
    Used to open a file and write the oputput
    def open_spider(self, spider):
        self.file = open("ars_items.json", "w")
    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item
    def close_spider(self, spider):
        self.file.close()
"""
