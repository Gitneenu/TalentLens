import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import UploadPage from "./pages/UploadPage";
import RankingPage from "./pages/RankingPage";
import Navbar from "./Components/Navbar";

function App() {
  return (
    <BrowserRouter>

      {/* 🔥 Navbar here (global) */}
      <Navbar />

      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/ranking" element={<RankingPage />} />
      </Routes>

    </BrowserRouter>
  );
}

export default App;