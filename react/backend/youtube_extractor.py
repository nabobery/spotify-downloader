import asyncio

import yt_dlp


class YouTubeLinksExtractor:
    def __init__(self):
        # ... existing initialization code ...
        self.semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent downloads

    async def download_audio_async(self, youtube_url, output_path):
        async with self.semaphore:  # This will limit concurrent downloads
            if self.download_ydl is None:
                ydl_opts = {**self.download_opts, "outtmpl": output_path}
                self.download_ydl = yt_dlp.YoutubeDL(ydl_opts)

            try:
                await asyncio.to_thread(self.download_ydl.download, [youtube_url])
                return True
            except Exception as e:
                print(f"Error downloading {youtube_url}: {str(e)}")
                return False
