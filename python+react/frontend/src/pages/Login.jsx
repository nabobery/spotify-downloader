import React from 'react';

function Login() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-primary-light">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-primary-dark mb-6">Welcome!</h2>
          <p className="text-primary-dark/70 mb-8">
            Connect your Spotify account to analyze your playlists and download songs
          </p>
          <a
            href="http://localhost:5000/login"
            className="inline-flex items-center justify-center space-x-2 bg-primary-medium text-white px-6 py-3 rounded-full hover:bg-primary-dark transition-colors w-full"
          >
            <svg className="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 14.5c-2.49 0-4.5-2.01-4.5-4.5S9.51 7.5 12 7.5s4.5 2.01 4.5 4.5-2.01 4.5-4.5 4.5zm0-5.5c-.55 0-1 .45-1 1s.45 1 1 1 1-.45 1-1-.45-1-1-1z"/>
            </svg>
            <span>Login with Spotify</span>
          </a>
        </div>
      </div>
    </div>
  );
}

export default Login;
