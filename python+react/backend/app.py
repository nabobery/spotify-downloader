import os
import time
import zipfile
import tempfile
from flask import Flask, request, redirect, render_template, send_file, url_for, session
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import yt_dlp
import urllib.parse
import json
import shutil

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Spotify API setup
SPOTIPY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SCOPE = 'playlist-read-private'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE
    )

def get_playlist_tracks(sp, playlist_url):
    playlist_id = playlist_url.split('/')[-1].split('?')[0]
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def download_audio(youtube_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

@app.route('/download_all', methods=['POST'])
def download_all():
    youtube_links = request.form.get('youtube_links')
    if not youtube_links:
        return "No YouTube links provided", 400
    
    # Step 1: URL decode
    decoded_urls = urllib.parse.unquote(youtube_links)

    # Step 2: Parse JSON
    youtube_links = json.loads(decoded_urls)

    print(youtube_links)

    # Create a temporary directory that will be automatically cleaned up
    temp_dir = tempfile.mkdtemp()
    
    try:
        for i, track in enumerate(youtube_links):
            output_path = os.path.join(temp_dir, f"{track['artist']} - {track['title']}.%(ext)s")
            try:
                download_audio(track['youtube_url'], output_path)
            except Exception as e:
                print(f"Error downloading {track['youtube_url']}: {str(e)}")

        # Create a zip file containing all downloaded tracks
        zip_path = os.path.join(temp_dir, 'playlist_audio.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in os.listdir(temp_dir):
                if file.endswith('.mp3'):
                    zipf.write(os.path.join(temp_dir, file), file)

        # Send the file and ensure it's deleted after sending
        response = send_file(zip_path, as_attachment=True, download_name='playlist_audio.zip')
        
        return response
    
    finally:
        # Ensure temporary directory is cleaned up
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Error cleaning up temporary directory: {str(e)}")

def search_and_download_youtube(artist, title):
    chrome_options = Options()
    chrome_options.headless = True  # Runs in headless mode (no GUI)
    driver = webdriver.Chrome(options=chrome_options)

    # Search for the video on YouTube
    driver.get(f"https://www.youtube.com/results?search_query={artist} {title}")
    video_element = driver.find_element(By.CSS_SELECTOR, "a#video-title")
    youtube_url = video_element.get_attribute("href")

    # Download the video
    driver.get(youtube_url)
    # Add code to download the video (additional code would be needed here)

    driver.quit()
    return youtube_url

@app.route('/')
def index():
    if not session.get('token_info'):
        return render_template('index.html', login_url=url_for('login'))
    else:
        sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
        playlists = sp.current_user_playlists()['items']
        return render_template('playlist.html', playlists=playlists, playlist=None) 

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for('index'))

@app.route('/analyze_playlist', methods=['POST'])
def analyze_playlist():
    session['token_info'], authorized = get_token()
    if not authorized:
        return redirect('/login')

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    playlist_url = request.form.get('playlist_url')

    if not playlist_url:
        return "No playlist URL provided", 400

    playlist = sp.playlist(playlist_url.split('/')[-1].split('?')[0])
    tracks = get_playlist_tracks(sp, playlist_url)

    youtube_links = []
    for track in tracks:
        track_info = track['track']
        artist = track_info['artists'][0]['name']
        title = track_info['name']
        youtube_url = search_and_download_youtube(artist, title)
        youtube_links.append({
            'artist': artist,
            'title': title,
            'youtube_url': youtube_url
        })

    return render_template('playlist.html', playlist=playlist, youtube_links=youtube_links)

def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    if not session.get('token_info', False):
        token_valid = False
        return token_info, token_valid

    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    if is_token_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

if __name__ == '__main__':
    app.run(debug=True)