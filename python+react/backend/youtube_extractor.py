import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse

class YouTubeLinksExtractor:
    def __init__(self, headless=True, max_workers=5):
        """
        Initialize the YouTube links extractor
        
        :param headless: Run browser in headless mode
        :param max_workers: Number of concurrent threads for searching
        """
        # Chrome options configuration
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument('--headless')  # Run in background
        
        # Additional performance and stability options
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        
        # Initialize the webdriver once
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=self.chrome_options
        )
        
        # Concurrency settings
        self.max_workers = max_workers

    def search_youtube_url(self, artist, title):
        """
        Search for a YouTube URL for a specific track
        
        :param artist: Artist name
        :param title: Track title
        :return: YouTube URL or None
        """
        try:
            # URL encode the search query
            search_query = urllib.parse.quote(f"{artist} {title}")
            search_url = f"https://www.youtube.com/results?search_query={search_query}"
            
            # Navigate to search results
            self.driver.get(search_url)
            
            # Wait for results and find the first video link
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, "a#video-title")
            
            # Return the first video URL if found
            return video_elements[0].get_attribute("href") if video_elements else None
        
        except Exception as e:
            print(f"Error searching for {artist} - {title}: {e}")
            return None

    def extract_youtube_links(self, tracks):
        """
        Extract YouTube links for multiple tracks concurrently
        
        :param tracks: List of track dictionaries
        :return: List of track info with YouTube links
        """
        youtube_links = []
        
        # Use ThreadPoolExecutor for concurrent searching
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Prepare futures for each track
            futures = {
                executor.submit(self.search_youtube_url, 
                                track['track']['artists'][0]['name'], 
                                track['track']['name']): track 
                for track in tracks
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(futures):
                original_track = futures[future]
                try:
                    youtube_url = future.result()
                    if youtube_url:
                        youtube_links.append({
                            'artist': original_track['track']['artists'][0]['name'],
                            'title': original_track['track']['name'],
                            'youtube_url': youtube_url
                        })
                except Exception as e:
                    print(f"Error processing track: {e}")
        
        return youtube_links

    def close(self):
        """
        Close the webdriver
        """
        if self.driver:
            self.driver.quit()

# Usage example
def process_tracks_using_youtube_extractor(tracks):
    extractor = YouTubeLinksExtractor(headless=True)
    try:
        youtube_links = extractor.extract_youtube_links(tracks)
        return youtube_links
    finally:
        extractor.close()