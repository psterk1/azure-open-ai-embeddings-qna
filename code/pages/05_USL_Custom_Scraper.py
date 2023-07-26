import streamlit as st
from streamlit_chat import message
from utilities.helper import LLMHelper
import traceback
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

usl_stats = f'https://www.fotmob.com/leagues/8972/stats/usl-championship/players'
urls = []
urls.append(usl_stats)

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
    st.session_state['filename'] = filename
    st.session_state['file_url'] = llm_helper.blob_client.upload_file(bytes_data, filename, content_type=content_type+charset)
    llm_helper.add_embeddings_lc(st.session_state['file_url'])
    st.write("Embeddings created successfully")

try:
    # Set page layout to wide screen and menu item
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App
	 Embedding testing application.
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    llm_helper = LLMHelper()

    st.write("Press the button below to execute the function:")

    # Add a button to execute the function when pressed
    if st.button("Create Embeddings"):
        create_embeddings_from_scraper()

except Exception as e:
    st.error(traceback.format_exc())