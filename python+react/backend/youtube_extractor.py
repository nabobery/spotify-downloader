import asyncio
import os

import yt_dlp


class YouTubeLinksExtractor:
    def __init__(self):
        """
        Initialize the YouTube links extractor

        :param headless: Run browser in headless mode
        :param max_workers: Number of concurrent threads for searching
        """

        self.ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "default_search": "ytsearch1",  # Only get first result
        }

        self.download_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        self.search_ydl = yt_dlp.YoutubeDL(self.ydl_opts)

    def extract_youtube_links_sync(self, tracks) -> list:
        youtube_links = []

        for track in tracks:
            youtube_url = self.search_youtube_url(
                track["track"]["artists"][0]["name"], track["track"]["name"]
            )
            if youtube_url:
                youtube_links.append(
                    {
                        "artist": track["track"]["artists"][0]["name"],
                        "title": track["track"]["name"],
                        "youtube_url": youtube_url,
                    }
                )

        return youtube_links

    # using asyncio.gather
    async def extract_youtube_links_async(self, tracks):
        youtube_links = []
        try:
            tasks = [
                asyncio.to_thread(
                    self.search_youtube_url,
                    track["track"]["artists"][0]["name"],
                    track["track"]["name"],
                )
                for track in tracks
            ]
            results = await asyncio.gather(*tasks)

            for track, youtube_url in zip(tracks, results):
                if youtube_url:
                    youtube_links.append(
                        {
                            "artist": track["track"]["artists"][0]["name"],
                            "title": track["track"]["name"],
                            "youtube_url": youtube_url,
                        }
                    )
        except Exception as e:
            print(f"Error processing tracks in function: {e}")
        return youtube_links

    def search_youtube_url(self, artist, title):
        """
        Search for a YouTube URL for a specific track

        :param artist: Artist name
        :param title: Track title
        :return: YouTube URL or None
        """
        try:
            result = self.search_ydl.extract_info(
                f"ytsearch1:{artist} {title}", download=False
            )

            if result and "entries" in result and result["entries"]:
                return f"https://www.youtube.com/watch?v={result['entries'][0]['id']}"
            return None

        except Exception as e:
            print(f"Error searching for {artist} - {title}: {e}")
            return None

    def _get_safe_filename(self, artist, title):
        # Remove or replace illegal characters
        unsafe_chars = '<>:"/\\|?*'
        safe_name = f"{artist} - {title}"
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, "_")
        # Add a unique identifier to prevent conflicts
        # unique_id = str(uuid.uuid4())[:8]
        # return f"{safe_name}_{unique_id}"
        return safe_name

    async def download_audio_async(self, youtube_url, artist, title, temp_dir):
        safe_filename = self._get_safe_filename(artist, title)
        output_path = os.path.join(temp_dir, f"{safe_filename}.%(ext)s")
        ydl_opts = {**self.download_opts, "outtmpl": output_path}
        download_ydl = yt_dlp.YoutubeDL(ydl_opts)

        try:
            await asyncio.to_thread(download_ydl.download, [youtube_url])
            return True
        except Exception as e:
            print(f"Error downloading {youtube_url}: {str(e)}")
            return False

    async def download_tracks_async(self, youtube_links, temp_dir):
        tasks = []
        for track in youtube_links:
            task = self.download_audio_async(
                track["youtube_url"], track["artist"], track["title"], temp_dir
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)
