from dotenv import load_dotenv

import pymysql
import os
import logging



class Mysql:
    def __init__(self):
        load_dotenv()

    @staticmethod
    def __connect():
        try:
            connection = pymysql.connect(
                host=os.getenv("hostname"),
                user=os.getenv("db_username"),
                password=os.getenv("db_password"),
                database=os.getenv("db_name"),
                cursorclass=pymysql.cursors.DictCursor
            )
            if (connection is None):
                raise Exception
            return connection

        except Exception as exception:
            logger = logging.getLogger()
            logger.error(f"Failed to connect to database: {exception}")

    def make_request(self, sql_request : str, is_need_data : bool):
        connection = Mysql.__connect()
        try:
            with connection.cursor() as cursor:
                response = cursor.execute(sql_request)
                connection.commit()
                if (is_need_data):
                    return cursor.fetchall()

                return True if response else False

        except Exception as exception:
            logger = logging.getLogger()
            logger.error(f"Failed to make request: {exception}")

        finally:
            connection.close()
