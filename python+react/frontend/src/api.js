import axios from 'axios';
import { useAuth } from './components/AuthContext';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use((config) => {
  const tokenInfo = JSON.parse(localStorage.getItem('spotify_token'));
  if (tokenInfo?.access_token) {
    config.headers.Authorization = `Bearer ${tokenInfo.access_token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh here if needed
      const { refreshToken } = useAuth();
      await refreshToken();

      // Retry the original request
      const originalRequest = error.config;
      return api(originalRequest);
    }
    return Promise.reject(error);
  }
);

export const getPlaylists = () => api.get('/playlists');
export const analyzePlaylist = (playlistUrl) =>
  api.post('/analyze_playlist', { playlist_url: playlistUrl });
export const downloadTracks = (youtubeLinks) =>
  api.post('/download_all', { youtube_links: youtubeLinks }, { responseType: 'blob' });

export default api;
