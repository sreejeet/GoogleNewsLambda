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

    # In case the key does not exists in the article, return empty string for the text attribute.
    # This keeps the parser code clean, although may not be the best solution for this case.
    class emptytext():
        text = ''

    # Keys to be parsed from each article
    keys = [
        'title'
        'link'
        'published_date'
        'description'
        'source'
    ]

    # Parse and store articles in memory first
    articles = []
    for item in ET.fromstring(response.text).findall('.//item'):
        articles.append({
            key: (item.find(key) or emptytext()).text for key in keys
        })

    # Then save each article into the database (AWS RDS)
    for article in articles:
        pass

    return {
        'statusCode': 200,
        'body': json.dumps(articles)
    }
