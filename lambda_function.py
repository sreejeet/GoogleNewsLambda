import json
import requests
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET


def lambda_handler(event, context):

    # Make the search term url-safe
    search_term = quote_plus(event['queryStringParameters']['search'])

    if not search_term:
        return {
            'statusCode': 200,
            'body': json.dumps('Nothing found!')
        }

    # Make a request to search for google news articles using the
    # query parameter 'search' as the keyword argument
    response = requests.get(
        f"https://news.google.com/rss/search?q={search_term}&hl=en-IN&gl=IN&ceid=IN:en")

    articles = []

    for item in ET.fromstring(response.text).findall('.//item'):
        articles.append({
            'title': item.find('title').text,
            'link': item.find('link').text,
            'published_date': item.find('pubDate').text,
            'description': item.find('description').text,
        })

    return {
        'statusCode': 200,
        'body': json.dumps(articles)
    }
