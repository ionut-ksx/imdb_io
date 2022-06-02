# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from imdb_io.items import Movie, Actor, MovieActors
import sqlite3
import sys
import ipdb
import json


class ImdbIoPipeline:
    def process_item(self, item, spider):
        return item


class SqlitePipeline:
    def open_spider(self, spider):

        # Create/connect to db
        self.con = sqlite3.connect("imdb.db")

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
            url TEXT,
            image_urls TEXT)
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
                """INSERT INTO movies (category,date_of_scraping,director,rating,release_year,title,top_cast,url,image_urls) VALUES (?,?,?,?,?,?,?,?,?)""",
                [
                    (
                        json.dumps(item["category"]),
                        json.dumps(item["date_of_scraping"]),
                        json.dumps(item["director"]),
                        json.dumps(item["rating"]),
                        json.dumps(item["release_year"]),
                        json.dumps(item["title"]),
                        json.dumps(item["top_cast"]),
                        json.dumps(item["url"]),
                        json.dumps(item["image_urls"]),
                    )
                ],
            )
        self.con.commit()

        if isinstance(item, Actor):
            self.cur.executemany(
                """INSERT INTO actors (filmography_movie_name,name,url_id) VALUES (?,?,?)""",
                # [(item["filmography_movie_name"], item["name"], item["url_id"])],
                [(json.dumps(item["filmography_movie_name"]), json.dumps(item["name"]), json.dumps(item["url_id"]))],
            )
        self.con.commit()

        if isinstance(item, MovieActors):
            self.cur.executemany(
                """INSERT INTO movie_actors (movie_url, actor_url) VALUES (?,?)""",
                [(json.dumps(item["movie_url"]), json.dumps(item["actor_url"]))],
            )

        return item

    def close_spider(self, spider):

        try:
            print("\n******* Request #1 **********")
            self.cur.execute(
                "SELECT category, COUNT(category) AS Gender FROM movies GROUP BY category ORDER BY Gender DESC LIMIT 5"
            )
            print("\nCategory || Occurrencee - Top 5")
            movie_name = self.cur.fetchall()
            for item in movie_name:
                print(item)

            print("\n******* Request #2 **********")
            self.cur.execute(
                "SELECT (CAST(SUBSTR(release_year,2,4) AS INTEGER)/100)*100 AS Decade,  COUNT(release_year) AS occur, release_year FROM movies GROUP BY release_year ORDER BY occur DESC LIMIT 1"
            )
            print("\nDecade || Occurrencee || Year")
            decade = self.cur.fetchone()
            print(decade)

            print("\n******* Request #3 **********")
            self.cur.execute("SELECT COUNT(name) AS occur, name from actors GROUP BY name ORDER BY occur DESC LIMIT 10")
            top_10_actors = self.cur.fetchall()
            print("\nRate || Actor name - Top 10")
            for actor in top_10_actors:
                print(actor)

            print("\n******* Request #4 **********")
            self.cur.execute(
                "SELECT  actor_url,  CAST(COUNT(DISTINCT(movie_url)) AS FLOAT)/CAST(COUNT(actor_url) AS FLOAT) AS percc  FROM movie_actors GROUP BY movie_url "
            )

            # result = sum(x) for x in percentage.value()
            # print(result)

        except sqlite3.Error as e:
            print("Error {}:".format(e.args[0]))
            sys.exit(1)

        finally:
            if self.con:
                self.con.commit()
                self.con.close()


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
