import logging
import streamlit as st
from utilities.helper import LLMHelper
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timezone
from zoneinfo import ZoneInfo

import azure.functions as func

usl_stats = f'https://www.fotmob.com/leagues/8972/stats/usl-championship/players'
urls = []
urls.append(usl_stats)

llm_helper = LLMHelper()

def create_embeddings_from_scraper():
    for url in  urls:
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            #headlines = soup.find_all('h2',{'class':'fa-text__title'})
            headlines = soup.find_all(id="__NEXT_DATA__")
            #headlines = soup.find_all(string="name")
            
            # Print the headlines
            for headline in headlines:
                #print(headline.text.strip())
                json_data = headline.text.strip() 
                # Parse the JSON data into a Python dictionary
                data = json.loads(json_data)
                #print(data['props']['pageProps']['stats']['players'][0])
                #f.write(data['props']['pageProps']['stats']['players'][0])
                metrics = data['props']['pageProps']['stats']['players']
                metric_data = ''
                for metric in metrics:
                    metric_name = metric['header']
                    #print(metric_name)
                    players = metric['topThree']
                    metric_data += "Player Name, Team, Rank," + metric_name + "\n"
                    for player in players:
                        player_name = player["name"]
                        team_name = player["teamName"]
                        rank = player["rank"]
                        rating = player["value"]
                        if metric_name == 'Top scorer':
                            metric_name = 'Goals'
                        player_data = f"{player_name}, {team_name}, rank: {rank}, {metric_name}: {rating}\n"
                        metric_data += player_data

        else:
            print('Failed to retrieve the webpage.')

    content_type = 'text/plain' 
    bytes_data = bytes(metric_data, 'utf-8')
    charset = ''
    current_timestamp = datetime.now(tz=ZoneInfo("America/Los_Angeles")).strftime('%Y-%m-%d_%H:%M:%S')
    filename = "usl_player_stats_" + current_timestamp
    file_url = llm_helper.blob_client.upload_file(bytes_data, filename, content_type=content_type+charset)
    llm_helper.add_embeddings_lc(file_url)

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(
        tzinfo=timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    try:
        logging.info("Start scraping and create embeddings")
        create_embeddings_from_scraper()
        logging.info("Finished scraping and created embeddings")
    except Exception as e:
        logging.error(e)
