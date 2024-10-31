import os
import time
import zipfile
import tempfile
from flask import Flask, request, jsonify, redirect, session, render_template_string, send_file, url_for
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from dotenv import load_dotenv
import yt_dlp

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)  # Enable CORS for all routes

# Spotify API setup
SPOTIPY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SCOPE = 'playlist-read-private'

# YouTube API setup
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

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

def search_youtube(query):
    request = youtube.search().list(
        q=query,
        type='video',
        part='id,snippet',
        maxResults=1
    )
    response = request.execute()
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        return f'https://www.youtube.com/watch?v={video_id}'
    return None

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

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Spotify Playlist Analyzer</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
            h1 { color: #1DB954; }
            form { margin-bottom: 20px; }
            input[type="text"] { width: 300px; padding: 5px; }
            input[type="submit"] { background-color: #1DB954; color: white; padding: 5px 10px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Spotify Playlist Analyzer</h1>
        {% if not session.get('token_info') %}
            <p>Please <a href="{{ url_for('login') }}">log in with Spotify</a> to use this service.</p>
        {% else %}
            <form action="{{ url_for('analyze_playlist') }}" method="post">
                <input type="text" name="playlist_url" placeholder="Enter Spotify Playlist URL" required>
                <input type="submit" value="Analyze Playlist">
            </form>
        {% endif %}
    </body>
    </html>
    """)

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

    playlist_id = playlist_url.split('/')[-1].split('?')[0]
    playlist = sp.playlist(playlist_id)
    tracks = get_playlist_tracks(sp, playlist_url)
    
    youtube_links = []
    for track in tracks:
        track_info = track['track']
        artist = track_info['artists'][0]['name']
        title = track_info['name']
        query = f'{artist} - {title}'
        youtube_link = search_youtube(query)
        youtube_links.append({
            'artist': artist,
            'title': title,
            'youtube_url': youtube_link
        })

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Playlist Analysis: {{ playlist['name'] }}</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
            h1, h2 { color: #1DB954; }
            img { max-width: 300px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #1DB954; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .download-btn { background-color: #1DB954; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Playlist Analysis: {{ playlist['name'] }}</h1>
        <img src="{{ playlist['images'][0]['url'] }}" alt="Playlist Cover">
        <h2>Playlist Stats</h2>
        <p><strong>Description:</strong> {{ playlist['description'] }}</p>
        <p><strong>Owner:</strong> {{ playlist['owner']['display_name'] }}</p>
        <p><strong>Total Tracks:</strong> {{ playlist['tracks']['total'] }}</p>
        <p><strong>Followers:</strong> {{ playlist['followers']['total'] }}</p>
        
        <h2>Tracks and YouTube Links</h2>
        <table>
            <tr>
                <th>Artist</th>
                <th>Title</th>
                <th>YouTube Link</th>
            </tr>
            {% for track in youtube_links %}
            <tr>
                <td>{{ track['artist'] }}</td>
                <td>{{ track['title'] }}</td>
                <td><a href="{{ track['youtube_url'] }}" target="_blank">YouTube Link</a></td>
            </tr>
            {% endfor %}
        </table>
        
        <form action="{{ url_for('download_all') }}" method="post">
            <input type="hidden" name="youtube_links" value="{{ youtube_links|tojson|urlencode }}">
            <input type="submit" value="Download All Tracks" class="download-btn">
        </form>
    </body>
    </html>
    """, playlist=playlist, youtube_links=youtube_links)

@app.route('/download_all', methods=['POST'])
def download_all():
    youtube_links = request.form.get('youtube_links')
    if not youtube_links:
        return "No YouTube links provided", 400

    youtube_links = eval(youtube_links)  # Convert string back to list of dicts

    with tempfile.TemporaryDirectory() as temp_dir:
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

        return send_file(zip_path, as_attachment=True, download_name='playlist_audio.zip')

def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    print(token_info, token_valid)
    return token_info, token_valid

if __name__ == '__main__':
    app.run(debug=True)