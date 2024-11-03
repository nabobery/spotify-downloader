import os
import shutil
import tempfile
import time
import zipfile
from functools import wraps

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
FRONTEND_URL = os.getenv("FRONTEND_URL")
SCOPE = "playlist-read-private"

youtube_extractor = YouTubeLinksExtractor()


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "No authorization token provided"}), 401

        token = auth_header.split(" ")[1]
        try:
            # Verify token with Spotify
            sp = spotipy.Spotify(auth=token)
            sp.current_user()  # This will fail if token is invalid
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401

    return decorated


def require_auth_async(f):
    @wraps(f)
    async def decorated_async(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "No authorization token provided"}), 401

        token = auth_header.split(" ")[1]
        try:
            # Verify token with Spotify
            sp = spotipy.Spotify(auth=token)
            sp.current_user()  # This will fail if token is invalid
            return await f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401

    return decorated_async


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=f"{FRONTEND_URL}/callback",
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
@require_auth
def get_playlists():
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]
    sp = spotipy.Spotify(auth=token)
    playlists = sp.current_user_playlists()["items"]
    return jsonify(playlists)


@app.route("/login")
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/refresh_token", methods=["POST"])
def refresh_token():
    try:
        data = request.json
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            return jsonify({"error": "No refresh token provided"}), 400

        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(refresh_token)

        return jsonify(token_info), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/callback")
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    return jsonify(token_info), 200


@app.route("/analyze_playlist", methods=["POST"])
@require_auth_async
async def analyze_playlist():
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]
    sp = spotipy.Spotify(auth=token)

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
