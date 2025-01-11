import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import time
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()


url = "https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_finals"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html')

table = soup.find('table',class_="sortable plainrowheaders wikitable")
headers = table.find_all('th')
headers_name = [data.text.strip() for data in headers][:7]
data_frame = pd.DataFrame(columns=headers_name)
data_in_rows = table.find_all('tr')

for row in data_in_rows[1:-1]:
    th_data = row.find_all('th')[0].find('a').contents[0]
    data = row.find_all('td')[:-1]
    individual_data = [item.text.strip() for item in data]
    individual_data.insert(0,th_data)

    length = len(data_frame)
    data_frame.loc[length] = individual_data

data_frame['Score'] = data_frame['Score'].astype(str)
data_frame['Score'] = data_frame['Score'].apply(lambda x: re.sub(r"\[n 3]", "", x))
data_frame['Attendance']=data_frame['Attendance'].str.replace(',','',regex=True)
data_frame = data_frame.astype({'Year': 'int32','Attendance' : 'int32'})

api_key = os.getenv('MY_API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)

def search_videos_in_playlist(playlist_id, keyword):
    next_page_token = None
    videos_found = []

    while True:
        playlist_items_request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        playlist_items_response = playlist_items_request.execute()

        for item in playlist_items_response['items']:
            video_title = item['snippet']['title']
            video_description = item['snippet']['description']
            video_id = item['snippet']['resourceId']['videoId']

            if keyword.lower() in video_title.lower() or keyword.lower() in video_description.lower():
                videos_found.append({
                    'title': video_title,
                    'video_url': f'https://www.youtube.com/watch?v={video_id}'
                })

        next_page_token = playlist_items_response.get('nextPageToken')
        if not next_page_token:
            break

    return videos_found

logos = {
    "England": "https://upload.wikimedia.org/wikipedia/en/thumb/8/8b/England_national_football_team_crest.svg/255px-England_national_football_team_crest.svg.png",
    "Italy": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Logo_Italy_National_Football_Team_-_2023.svg/203px-Logo_Italy_National_Football_Team_-_2023.svg.png",
    "Germany": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e3/DFBEagle.svg/293px-DFBEagle.svg.png",
    "France": "https://upload.wikimedia.org/wikipedia/en/thumb/1/12/France_national_football_team_seal.svg/225px-France_national_football_team_seal.svg.png",
    "Spain": "https://upload.wikimedia.org/wikipedia/en/thumb/3/39/Spain_national_football_team_crest.svg/218px-Spain_national_football_team_crest.svg.png",
    "Argentina": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c1/Argentina_national_football_team_logo.svg/210px-Argentina_national_football_team_logo.svg.png",
    "Brazil" : "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Brazilian_Football_Confederation_logo.svg/1200px-Brazilian_Football_Confederation_logo.svg.png",
    "Uruguay" : "https://upload.wikimedia.org/wikipedia/en/thumb/4/43/Uruguay_national_football_team_seal.svg/1200px-Uruguay_national_football_team_seal.svg.png"
}



st.set_page_config(
    page_title="List of Fifa World Cup Finals",
    page_icon=":soccer:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Welcome to FifaWC App!")
st.write("This app displays a list of FIFA World Cup finals using Streamlit")


with st.sidebar:
  year = st.slider("Choose the year of final?", 1930, 2022, 1950,4)

tab1, tab2, tab3 = st.tabs(["Result", "Highlights", "Statistics"])


with tab1:
  with st.spinner("Searching for the final"):
      time.sleep(1)
      if year:
        if year not in (1942,1946):
          st.info('a.e.t.	Match went to extra time\n\npen.	Match was won on a penalty shoot-out')
          st.table(data_frame[data_frame['Year']==year])
          winner = data_frame[data_frame['Year']==year].values[0][1]
          if st.button("Congratulations", icon="🌟"):
             for country, logo in logos.items():
                  if winner == country:
                      st.image(logo, width=150) 
                      st.balloons()

        else:
          st.info("The 1942 and 1946 World Cups were canceled due to World War II")  
      else:
        st.warning('Choose the year of final')


with tab2:
     playlist_id = 'PLCGIzmTE4d0htBvG2QNpJCeYoOJRuTKCG'
     keyword = str(year)
     videos = search_videos_in_playlist(playlist_id, keyword)
     if videos:
         if keyword not in ('1934','1970'):
            st.video(videos[0]['video_url'])
         else:
             st.video(videos[1]['video_url'])
         # for video in videos:
        #     st.video(video['video_url'])
     else:
        print("No videos found with the keyword.")


with tab3:
  if year not in (1942,1946):
      url2 = f"https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup"
      response2 = requests.get(url2)
      soup2 = BeautifulSoup(response2.text, 'html')
      table2 = soup2.find('table',class_="infobox vcalendar")
      headers2 = table2.find_all('tr')
      all_th_tags = []
      for header in headers2:
          all_th_tags.extend(header.find_all('th')) 

      hosts = []
      top_scorers = []
      best_player = []
      best_young_player = []
      best_gk = []
      for i in all_th_tags:
          if i.text.strip() == "Top scorer(s)":
              top_scorers_element = i.find_next_sibling("td")
              if top_scorers_element:
                  top_scorers = top_scorers_element.text.strip()
      for i in all_th_tags:
          if i.text.strip() == "Host country":
              hosts_element = i.find_next_sibling("td")
              if hosts_element:
                  hosts = hosts_element.text.strip()
      for i in all_th_tags:
          if i.text.strip() == "Best player(s)":
              bp_element = i.find_next_sibling("td")
              if bp_element:
                  best_player = bp_element.text.strip()        
      for i in all_th_tags:
          if i.text.strip() == "Best young player":
              byp_element = i.find_next_sibling("td")
              if byp_element:
                  best_young_player = byp_element.text.strip()
      for i in all_th_tags:
          if i.text.strip() == "Best goalkeeper":
              bgk_element = i.find_next_sibling("td")
              if bgk_element:
                  best_gk = bgk_element.text.strip()   

      data = {'Host Country': [hosts],
              'Top Scorer(s)': [top_scorers],
            'Best Player(s)': [best_player],
            'Best Young Player': [best_young_player],
            'Best Goalkeeper': [best_gk]}
      df = pd.DataFrame(data)
      for col in ['Host Country', 'Top Scorer(s)', 'Best Player(s)', 'Best Young Player', 'Best Goalkeeper']:
        df.loc[df[col].str.len() == 0, col] = 'At that time, this award had not been created'
        df[col] = df[col].astype(str).apply(lambda x: re.sub(r"\[\d+\]", "", x))
      
      if year == 2002:
        df['Host Country'] = 'South Korea and Japan'
      elif year == 1974:
        df['Host Country'] = 'West Germany'
      
      

      st.table(df)
      


      facts = {
      "1930": "The first-ever FIFA World Cup; Uruguay also celebrated its centenary of independence. There were only 13 teams, and matches were played in two stadiums.",
      "1934": "The first World Cup with a qualification phase. The tournament featured 16 teams, and Italy's victory was the first of their four World Cup titles.",
      "1938": "The last World Cup before WWII; Austria was annexed by Nazi Germany, reducing the number of teams to 15.",
      "1950": "No single final match; instead, a final round-robin group was played. Uruguay's dramatic win over Brazil in the 'Maracanazo' is legendary.",
      "1954": "The 'Miracle of Bern,' where West Germany upset Hungary, who had been unbeaten for four years.",
      "1958": "Brazil's first World Cup win, marked by the emergence of Pelé, who was only 17 at the time. First World Cup televised in color.",
      "1962": "Brazil won their second consecutive World Cup, with Garrincha leading the team after Pelé's injury.",
      "1966": "England’s only World Cup win, marked by Geoff Hurst’s hat-trick in the final. It was also the first World Cup with a third-place play-off.",
      "1970": "Brazil’s third World Cup victory, ensuring them the Jules Rimet Trophy permanently. Brazil’s attacking style became iconic.",
      "1974": "West Germany won their second World Cup, while the Netherlands introduced the 'Total Football' style of play.",
      "1978": "Argentina’s first World Cup win, with the host nation overcoming the Netherlands in the final after extra time.",
      "1982": "Italy’s third World Cup win, with memorable attacking football, including Paolo Rossi’s Golden Boot.",
      "1986": "Argentina’s second World Cup, with Diego Maradona’s famous 'Hand of God' and 'Goal of the Century' against England.",
      "1990": "The tournament was marked by defensive tactics and many low-scoring games. West Germany claimed their third World Cup.",
      "1994": "Brazil’s fourth World Cup victory, with a penalty shootout final. It was the first World Cup held in the United States.",
      "1998": "France’s first World Cup win, led by Zinedine Zidane’s two goals in the final. It was the first tournament with 32 teams.",
      "2002": "Brazil’s fifth World Cup victory. It was the first World Cup co-hosted by two countries, and Ronaldo’s comeback was a key highlight.",
      "2006": "Italy’s fourth World Cup victory, with the final remembered for Zinedine Zidane’s headbutt and red card.",
      "2010": "Spain’s first World Cup win, with Andrés Iniesta scoring the winning goal in the final. First World Cup held in Africa.",
      "2014": "Germany’s fourth World Cup win. The tournament was overshadowed by Germany’s 7-1 victory over Brazil in the semi-finals.",
      "2018": "France’s second World Cup win. The final was a thrilling 4-2 victory over Croatia, with Kylian Mbappé emerging as a star.",
      "2022": "Argentina’s third World Cup win, with Lionel Messi cementing his legacy in the greatest World Cup final against France, which ended in a 3-3 draw and a penalty shootout."
    }

      images = {
      "1930": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Uruguay_national_football_team_1930.jpg/1200px-Uruguay_national_football_team_1930.jpg",
      "1934": "https://i.ytimg.com/vi/EBwZv0eFrCM/maxresdefault.jpg",
      "1938": "https://d31xsmoz1lk3y3.cloudfront.net/games/imgur/COc6NG5.jpg",
      "1950": "https://assets.goal.com/images/v3/blt53f821adebfe0c84/bb7532e89fefe5c10623ebf6fe8627feba580c06.jpg?auto=webp&format=pjpg&width=1200&quality=60",
      "1954": "https://assets.goal.com/images/v3/blt4bb68e757b329ec1/morlock.jpg?auto=webp&format=pjpg&width=1200&quality=60",
      "1958": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT-rnJhhOwgnY8oKxGzdcButvw8WsDr9Zft_w&s",
      "1962": "https://assets.goal.com/images/v3/bltae91457e746effc4/battle-of-santiago.jpg?auto=webp&format=pjpg&width=1200&quality=60",
      "1966": "https://media.gettyimages.com/id/540689399/photo/1966-fifa-world-cup-in-england-final-at-wembley-germany-2-4-england-germany-players-are.jpg?s=612x612&w=gi&k=20&c=qVCZnVj3PuYjBQRRPCAh1ClV8apBOVatpt525R-6cpg=",
      "1970": "https://americasquarterly.org/wp-content/uploads/2022/10/GettyImages-1227541383-scaled.jpg",
      "1974": "https://www.sportsnet.ca/wp-content/uploads/2014/06/WC_1974.jpg",
      "1978": "https://e0.365dm.com/18/05/1600x900/skysports-argentina-world-cup-1978_4323128.jpg?20180528203151",
      "1982": "https://assets.goal.com/images/v3/blt7e92bf9e8f74887c/rossi.jpg?auto=webp&format=pjpg&width=1200&quality=60",
      "1986": "https://assets.goal.com/images/v3/blte6928dc31d64673f/913b5c3983c54fe370a27bd7161502df55e57329.jpg?auto=webp&format=pjpg&width=1200&quality=60",
      "1990": "https://static.toiimg.com/thumb/msid-75389628,width-1280,height-720,resizemode-4/75389628.jpg",
      "1994": "https://i.ytimg.com/vi/wMMDWrhD7yY/maxresdefault.jpg",
      "1998": "https://media.cnn.com/api/v1/images/stellar/prod/180601162721-zidane-world-cup.jpg?q=w_3042,h_2274,x_0,y_0,c_fill",
      "2002": "https://i.guim.co.uk/img/media/fd9a2c59a1c1c606cca2c1e4c6e2811363917108/0_127_2899_2012/master/2899.jpg?width=445&dpr=1&s=none&crop=none",
      "2006": "https://i.guim.co.uk/img/static/sys-images/Guardian/Pix/pictures/2009/5/15/1242406770895/Zinedine-Zidanes-headbutt-002.jpg?width=465&dpr=1&s=none&crop=none",
      "2010": "https://assets.goal.com/images/v3/blt84e8e0a8b8beb52a/0d76aca0ac51c4fb86021ca444611fb08c3f1e8c.jpg?auto=webp&format=pjpg&width=3840&quality=60",
      "2014": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Germany_and_Argentina_face_off_in_the_final_of_the_World_Cup_2014_-2014-07-13_%286%29.jpg/640px-Germany_and_Argentina_face_off_in_the_final_of_the_World_Cup_2014_-2014-07-13_%286%29.jpg",
      "2018": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/France_champion_of_the_Football_World_Cup_Russia_2018.jpg/640px-France_champion_of_the_Football_World_Cup_Russia_2018.jpg",
      "2022": "https://media.cnn.com/api/v1/images/stellar/prod/221219105607-messi-crowd-world-cup-121822.jpg?q=w_3000,c_fill"
    }



      with st.expander("Notable facts"):
        for k,v in facts.items():
            if k == str(year):
              st.write(v)

        for k,v in images.items():
            if k == str(year):
              st.image(v)

  else:
    st.info("The 1942 and 1946 World Cups were canceled due to World War II")  






