import os
import shutil
import tempfile
import time
import zipfile

import spotipy
from flask import Flask, jsonify, redirect, request, send_file, session
from flask_cors import CORS
from spotipy.oauth2 import SpotifyOAuth
from youtube_extractor import YouTubeLinksExtractor

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# Spotify API setup
SPOTIPY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")
SCOPE = "playlist-read-private"

youtube_extractor = YouTubeLinksExtractor()


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
    )


def get_playlist_tracks(sp, playlist_url):
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    results = sp.playlist_tracks(playlist_id)
    tracks = results["items"]
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])
    return tracks


@app.route("/download_all", methods=["POST"])
async def download_all():
    data = request.json
    youtube_links = data.get("youtube_links")
    if not youtube_links:
        return "No YouTube links provided", 400

    temp_dir = tempfile.mkdtemp()

    try:
        await youtube_extractor.download_tracks_async(youtube_links, temp_dir)

        zip_path = os.path.join(temp_dir, "playlist_audio.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in os.listdir(temp_dir):
                if file.endswith(".mp3"):
                    zipf.write(os.path.join(temp_dir, file), file)

        response = send_file(
            zip_path, as_attachment=True, download_name="playlist_audio.zip"
        )
        return response

    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Error cleaning up temporary directory: {str(e)}")


@app.route("/playlists")
def get_playlists():
    if not session.get("token_info"):
        return jsonify({"authenticated": False}), 401

    sp = spotipy.Spotify(auth=session.get("token_info").get("access_token"))
    playlists = sp.current_user_playlists()["items"]
    return jsonify(playlists)


@app.route("/login")
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/callback")
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(FRONTEND_URL)


@app.route("/analyze_playlist", methods=["POST"])
async def analyze_playlist():
    session["token_info"], authorized = get_token()
    if not authorized:
        return redirect("/login")

    sp = spotipy.Spotify(auth=session.get("token_info").get("access_token"))
    data = request.json
    playlist_url = data.get("playlist_url")

    if not playlist_url:
        return jsonify({"error": "No playlist URL provided"}), 400

    try:
        playlist = sp.playlist(playlist_url.split("/")[-1].split("?")[0])
        tracks = get_playlist_tracks(sp, playlist_url)

        youtube_links = await youtube_extractor.extract_youtube_links_async(tracks)

        if not youtube_links:
            return jsonify({"error": "No YouTube links found"}), 400

        return jsonify({"playlist": playlist, "youtube_links": youtube_links})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    if not session.get("token_info", False):
        token_valid = False
        return token_info, token_valid

    now = int(time.time())
    is_token_expired = session.get("token_info").get("expires_at") - now < 60

    if is_token_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(
            session.get("token_info").get("refresh_token")
        )

    token_valid = True
    return token_info, token_valid


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
