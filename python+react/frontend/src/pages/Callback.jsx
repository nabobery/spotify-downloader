import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import api from '../api';

function Callback() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  useEffect(() => {
    const code = new URLSearchParams(location.search).get('code');
    if (code) {
      const getToken = async () => {
        try {
          const response = await api.get(`/callback?code=${code}`);
          if (response.data) {
            login(response.data);
            navigate('/');
          }
        } catch (error) {
          console.error('Error during callback:', error);
          navigate('/login');
        }
      };
      getToken();
    }
  }, [location, login, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p>Logging you in...</p>
    </div>
  );
}

export default Callback;
