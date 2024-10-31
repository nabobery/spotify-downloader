import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import PlaylistAnalysis from "./pages/PlaylistAnalysis";

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen bg-primary-light min-w-screen">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/playlist/:id" element={<PlaylistAnalysis />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;