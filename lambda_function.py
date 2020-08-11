import json
import requests
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET


def lambda_handler(event, context):

    # Make the search term url-safe
    search_term = event['queryStringParameters']['search']

    if not search_term:
        return {
            'statusCode': 200,
            'body': json.dumps('Nothing found!')
        }

    # Make a request to search for google news articles using the
    # query parameter 'search' as the keyword argument
    response = requests.get(
        f"https://news.google.com/rss/search?q={quote_plus(search_term)}&hl=en-IN&gl=IN&ceid=IN:en")

    # Parse and store articles in memory first
    articles = []
    for item in ET.fromstring(response.text).findall('.//item'):
        articles.append({
            'title': item.find('title').text if item.find('title') != None else '',
            'link': item.find('link').text if item.find('link') != None else '',
            'published_date': item.find('pubDate').text if item.find('pubDate') != None else '',
            'description': item.find('description').text if item.find('description') != None else '',
            'source': item.find('source').text if item.find('source') != None else '',
        })

    # Then save each article into the database (AWS RDS)
    for article in articles:
        pass

    respons_json = {
        'search_term': search_term,
        'articles_retrieved': len(articles),
    }

    return {
        'statusCode': 200,
        'body': json.dumps(respons_json)
    }
