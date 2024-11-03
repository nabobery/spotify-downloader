import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PlaylistCard from "../components/PlaylistCard";
import axios from "axios";

function Home() {
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const fetchPlaylists = async () => {
      try {
        const response = await axios.get(`${API_URL}/playlists`, {
          withCredentials: true,
        });
        setPlaylists(response.data);
      } catch (error) {
        if (error.response?.status === 401) {
          navigate("/login");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchPlaylists();
  }, [navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-medium mb-4"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-primary-dark mb-8">
        Your Spotify Playlists
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {playlists.map((playlist) => (
          <PlaylistCard key={playlist.id} playlist={playlist} />
        ))}
      </div>
    </div>
  );
}

export default Home;
