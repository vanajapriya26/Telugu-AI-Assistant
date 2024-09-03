import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from googleapiclient.discovery import build

# Replace with your actual API keys
GOOGLE_API_KEY = ''
SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''
YOUTUBE_API_KEY = ''

# Initialize the YouTube API client
def initialize_youtube_client(api_key):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        return youtube
    except Exception as e:
        print(f"Error initializing YouTube client: {e}")
        return None

# Initialize the Spotify client
def initialize_spotify_client(client_id, client_secret):
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
        return sp
    except Exception as e:
        print(f"Error initializing Spotify client: {e}")
        return None

# Function to search for a song on YouTube
def search_youtube(query, youtube_client):
    if not youtube_client:
        return 'YouTube client not initialized.'
    
    try:
        request = youtube_client.search().list(
            part='snippet',
            q=query,
            type='video',
            order='relevance'
        )
        response = request.execute()
        video_id = response['items'][0]['id']['videoId']
        return f'https://www.youtube.com/watch?v={video_id}'
    except Exception as e:
        return f'Error searching YouTube: {e}'

# Function to search for a song on Spotify
def search_spotify(query, spotify_client):
    if not spotify_client:
        return 'Spotify client not initialized.'
    
    try:
        result = spotify_client.search(q=query, type='track', limit=1)
        track = result['tracks']['items'][0]
        return track['external_urls']['spotify']
    except Exception as e:
        return f'Error searching Spotify: {e}'

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=['command'],
    template='Process the command: {command}'
)

# Initialize the Google Generative AI LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key=GOOGLE_API_KEY
)

# Define a function to handle the request
def handle_request(command):
    response = llm.run(prompt_template.format(command=command))
    return response

# Function to process commands using Langchain
def process_command(command):
    youtube_client = initialize_youtube_client(YOUTUBE_API_KEY)
    spotify_client = initialize_spotify_client(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
    
    command = command.lower()
    
    if 'play' in command and 'from youtube' in command:
        song_details = command.replace('play', '').replace('from youtube', '').strip()
        video_url = search_youtube(song_details, youtube_client)
        
        if video_url.startswith('https://'):
            webbrowser.open(video_url)
            return f'Playing your song on YouTube: {video_url}'
        else:
            return video_url
    elif 'play' in command and 'spotify' in command:
        song_details = command.replace('play', '').replace('spotify', '').strip()
        track_url = search_spotify(song_details, spotify_client)
        
        if track_url.startswith('https://'):
            webbrowser.open(track_url)
            return f'Playing your song on Spotify: {track_url}'
        else:
            return track_url
    else:
        return 'Command not recognized. Please try again.'

def main():
    while True:
        user_input = input("Enter your command: ")
        response = process_command(user_input)
        print(response)

if __name__ == "__main__":
    main()
