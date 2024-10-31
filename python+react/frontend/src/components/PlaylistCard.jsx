import { useNavigate } from "react-router-dom";

function PlaylistCard({ playlist }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/playlist/${playlist.id}`)}
      className="bg-primary rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 cursor-pointer"
    >
      <div className="aspect-square">
        {playlist.images?.[0] && (
          <img
            src={playlist.images[0].url}
            alt={playlist.name}
            className="w-full h-full object-cover"
          />
        )}
      </div>
      <div className="p-4">
        <h3 className="font-bold text-xl text-primary-dark mb-2">
          {playlist.name}
        </h3>
        <p className="text-primary-medium">{playlist.tracks.total} tracks</p>
        {playlist.description && (
          <p className="text-primary-dark/70 mt-2 text-sm">
            {playlist.description}
          </p>
        )}
      </div>
    </div>
  );
}

export default PlaylistCard;
