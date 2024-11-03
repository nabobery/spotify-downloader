import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import TrackList from "../components/TrackList";

function PlaylistAnalysis() {
  const [playlistData, setPlaylistData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { id } = useParams();
  const navigate = useNavigate();
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const analyzePlaylist = async () => {
      try {
        const response = await axios.post(
          `${API_URL}/analyze_playlist`,
          {
            playlist_url: `https://open.spotify.com/playlist/${id}`,
          },
          { withCredentials: true }
        );
        setPlaylistData(response.data);
      } catch (error) {
        if (error.response?.status === 401) {
          navigate("/login");
        } else {
          setError("Failed to analyze playlist. Please try again.");
        }
      } finally {
        setLoading(false);
      }
    };

    analyzePlaylist();
  }, [id, navigate]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-medium mb-4"></div>
        <p className="text-primary-dark">Analyzing playlist...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button
            onClick={() => navigate("/")}
            className="text-primary-medium hover:text-primary-dark"
          >
            Back to playlists
          </button>
        </div>
      </div>
    );
  }

  const { playlist, youtube_links } = playlistData;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <button
        onClick={() => navigate("/")}
        className="flex items-center text-primary-medium hover:text-primary-dark mb-6"
      >
        <svg className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path
            fillRule="evenodd"
            d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
            clipRule="evenodd"
          />
        </svg>
        Back to playlists
      </button>

      <div className="bg-primary rounded-lg shadow-md p-6 mb-8">
        <div className="flex flex-col md:flex-row md:space-x-8">
          {playlist.images?.[0] && (
            <img
              src={playlist.images[0].url}
              alt={playlist.name}
              className="w-full md:w-64 h-64 object-cover rounded-lg mb-6 md:mb-0"
            />
          )}
          <div>
            <h1 className="text-4xl font-bold text-primary-dark mb-4">
              {playlist.name}
            </h1>
            <p className="text-primary-medium mb-2">{playlist.description}</p>
            <p className="text-primary-medium mb-2">
              <span className="font-semibold">Created by:</span>{" "}
              {playlist.owner.display_name}
            </p>
            <p className="text-primary-medium">
              <span className="font-semibold">Total tracks:</span>{" "}
              {playlist.tracks.total}
            </p>
          </div>
        </div>
      </div>

      <TrackList tracks={youtube_links} />
    </div>
  );
}

export default PlaylistAnalysis;
