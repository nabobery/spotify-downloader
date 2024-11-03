import { useState } from "react";
import axios from "axios";

function TrackList({ tracks }) {
  const [downloading, setDownloading] = useState(false);
  const API_URL = import.meta.env.VITE_API_URL;

  const handleDownloadAll = async () => {
    try {
      setDownloading(true);
      const response = await axios.post(
        `${API_URL}/download_all`,
        { youtube_links: tracks },
        {
          responseType: "blob",
          withCredentials: true,
        }
      );

      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "playlist_audio.zip");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Download failed:", error);
      alert("Failed to download tracks. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="bg-primary rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-primary-dark">Tracks</h2>
        <button
          onClick={handleDownloadAll}
          disabled={downloading}
          className={`
            flex items-center space-x-2 px-4 py-2 rounded-full text-white
            ${
              downloading
                ? "bg-primary-medium/50 cursor-not-allowed"
                : "bg-primary-medium hover:bg-primary-dark"
            }
          `}
        >
          {downloading ? (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-medium mb-4"></div>
              <span>Downloading...</span>
            </>
          ) : (
            <>
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Download All</span>
            </>
          )}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-primary-light">
              <th className="px-6 py-3 text-left text-xs font-medium text-primary-dark uppercase tracking-wider">
                Artist
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-primary-dark uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-primary-dark uppercase tracking-wider">
                YouTube Link
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-primary-light">
            {tracks.map((track, index) => (
              <tr key={index} className="hover:bg-primary-light/50">
                <td className="px-6 py-4 whitespace-nowrap text-primary-dark">
                  {track.artist}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-primary-dark">
                  {track.title}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <a
                    href={track.youtube_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-medium hover:text-primary-dark"
                  >
                    Watch on YouTube
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TrackList;
