import os
import time
import zipfile
import tempfile
from flask import Flask, request, redirect, render_template, send_file, url_for, session, jsonify
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
from youtube_extractor import process_tracks_using_youtube_extractor

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

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
    data = request.json
    youtube_links = data.get('youtube_links')
    if not youtube_links:
        return "No YouTube links provided", 400

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
    
@app.route('/playlists')
def get_playlists():
    if not session.get('token_info'):
        return jsonify({'authenticated': False}), 401
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    playlists = sp.current_user_playlists()['items']
    return jsonify(playlists)

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
    return redirect('http://localhost:5173')

@app.route('/analyze_playlist', methods=['POST'])
def analyze_playlist():
    session['token_info'], authorized = get_token()
    if not authorized:
        return redirect('/login')

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    data = request.json  # Change from form to json
    playlist_url = data.get('playlist_url')

    if not playlist_url:
        return jsonify({'error':"No playlist URL provided"}), 400
    
    try:
        playlist = sp.playlist(playlist_url.split('/')[-1].split('?')[0])
        tracks = get_playlist_tracks(sp, playlist_url)

        youtube_links = process_tracks_using_youtube_extractor(tracks)

        if not youtube_links:
            return jsonify({'error': 'No YouTube links provided'}), 400

        return jsonify({
            'playlist': playlist,
            'youtube_links': youtube_links
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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