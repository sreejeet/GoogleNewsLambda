import logging
import json
import requests
from urllib.parse import quote_plus
from dateutil import parser
import xml.etree.ElementTree as ET
import pymysql.cursors
import os
import sys


DB_HOSTNAME = os.environ['DB_HOSTNAME']
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWD = os.environ['DB_PASSWD']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


try:
    DB_CON = pymysql.connect(host=DB_HOSTNAME,
                             user=DB_USERNAME,
                             passwd=DB_PASSWD,
                             db='news',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
except Exception as e:
    logger.error(
        "ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")


def lambda_handler(event, context):
    """ Route to the required function based on the resource
    that was used to call this lambda endpoint.
    """

    if event['resource'][1:] == 'search-and-store':
        return search_and_store(event['queryStringParameters']['search'])
    elif event['resource'][1:] == 'search-and-retrieve':
        return search_and_retrieve(event['queryStringParameters']['search'])

    return {
        'statusCode': 400,
        'body': json.dumps("Unknown event")
    }


def search_and_retrieve(search_term):
    """ Search and return articles with the provided search term
    from the local database
    """

    articles = []

    with DB_CON.cursor() as cursor:
        sql = f"""
        select
            news_id, title, link, description, source, DATE_FORMAT(published_date, '%d-%m-%Y %H:%i:%s') as published_date
        from news
            where title like '%{search_term}%'"""
        cursor.execute(sql)
        articles = cursor.fetchall()

    logger.info(f"Found {len(articles)} articles")

    respons_json = {
        'search_term': search_term,
        'articles_found': len(articles),
        'articles': articles,
    }

    return {
        'statusCode': 200,
        'body': json.dumps(respons_json)
    }


def search_and_store(search_term):
    """ Search articles with the provided search term from google
    and store them in local database.
    """

    # Return empty if search_term is a NoneType
    if search_term == None:
        respons_json = {
            'search_term': "",
            'articles_retrieved': 0,
        }
        return {
            'statusCode': 400,
            'body': json.dumps(respons_json)
        }

    # Make a request to search for google news articles using the
    # query parameter 'search' as the keyword argument
    response = requests.get(
        f"https://news.google.com/rss/search?q={quote_plus(search_term)}&hl=en-IN&gl=IN&ceid=IN:en")

    # Parse and store articles in memory
    articles = []

    # Just to be on the safe side, Limit to first 100 news articles,
    # altough google never sends more than 100 articles per search request.
    for item in ET.fromstring(response.text).findall('.//item')[:100]:

        # Converting date to mysql date format
        try:
            date = item.find('pubDate').text if item.find(
                'pubDate') != None else ''
            date = parser.parse(date)
            date = date.strftime("%Y-%m-%d %H:%M:%S")
        except:
            # Very unlikely that date cannot be parsed.
            # Stop execution if this happens
            logger.error("Date parse err")
            sys.exit()

        articles.append({
            'title': item.find('title').text if item.find('title') != None else '',
            'link': item.find('link').text if item.find('link') != None else '',
            'published_date': date,
            'description': item.find('description').text if item.find('description') != None else '',
            'source': item.find('source').text if item.find('source') != None else '',
            'source_link': item.find('source').attrib['url'] if item.find('source').text and item.find('source').attrib else '',
        })

    articles_retrieved_count = len(articles)
    logger.info(f"Got {articles_retrieved_count} articles")

    with DB_CON.cursor() as cursor:

        data = []
        values_placeholders = []
        for article in articles:
            data.append(article['title'])
            data.append(article['link'])
            data.append(article['published_date'])
            data.append(article['description'])
            data.append(article['source'])
            data.append(article['source_link'])
            values_placeholders.append("(%s, %s, %s, %s, %s, %s)")

        values_placeholders = ", ".join(values_placeholders)

        # Insert all articles in a single DB query
        sql = """INSERT IGNORE INTO `news`
                (`title`,`link`,`published_date`,`description`,`source`, `source_link`)
                VALUES """ + values_placeholders + ";"

        cursor.execute(sql, data)
        logger.info("START DB Says")
        logger.info(cursor.fetchall())
        logger.info("END DB Says")

    # Connection is not autocommit by default.
    # Commit to save changes.
    DB_CON.commit()
    del articles

    respons_json = {
        'search_term': search_term,
        'articles_retrieved': articles_retrieved_count,
    }

    return {
        'statusCode': 200,
        'body': json.dumps(respons_json)
    }
