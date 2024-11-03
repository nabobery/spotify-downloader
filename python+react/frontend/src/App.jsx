import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Callback from "./pages/Callback";
import PlaylistAnalysis from "./pages/PlaylistAnalysis";
import { AuthProvider } from "./components/AuthContext";

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="flex flex-col min-h-screen bg-primary-light min-w-screen">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/callback" element={<Callback />} />
          <Route path="/playlist/:id" element={<PlaylistAnalysis />} />
        </Routes>
      </div>
    </Router>
    </AuthProvider>
  );
}

export default App;
