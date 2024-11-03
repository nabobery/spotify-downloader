import { Link, useLocation } from "react-router-dom";

function Navbar() {
  const location = useLocation();
  const API_URL = import.meta.env.VITE_API_URL;

  return (
    <nav className="bg-primary shadow-md">
      <div className="flex flex-row justify-between max-w-7xl mx-auto px-4">
        <div className="flex flex-row items-center h-16">
          <Link to="/" className="flex flex-row gap-x-4 items-center space-x-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="text-primary-dark"
            >
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 14.5c-2.49 0-4.5-2.01-4.5-4.5S9.51 7.5 12 7.5s4.5 2.01 4.5 4.5-2.01 4.5-4.5 4.5zm0-5.5c-.55 0-1 .45-1 1s.45 1 1 1 1-.45 1-1-.45-1-1-1z" />
            </svg>
            <span className="px-4 font-bold text-xl text-primary-dark">
              Spotify Playlist Analyzer
            </span>
          </Link>
        </div>

        {location.pathname !== "/login" && (
          <div className="flex flex-row gap-x-8 items-center space-x-4">
            <Link
              to="/"
              className="text-primary-medium hover:text-primary-dark transition-colors"
            >
              My Playlists
            </Link>
            <a
              href={`${API_URL}/login`}
              className="bg-primary-medium text-white px-4 py-2 rounded-full hover:bg-primary-dark transition-colors"
            >
              Login with Spotify
            </a>
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
