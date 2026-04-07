import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();

  const linkStyle = (path) =>
    `px-4 py-2 rounded ${
      location.pathname === path
        ? "bg-blue-600 text-white"
        : "text-gray-300 hover:bg-gray-800"
    }`;

  return (
    <nav className="bg-[#0f1a2b] text-white px-8 py-4 flex justify-between items-center shadow-md">
      
      <h1 className="text-xl font-bold">
        TalentLens
      </h1>

      <div className="flex gap-4">
        <Link to="/" className={linkStyle("/")}>
          Dashboard
        </Link>

        <Link to="/upload" className={linkStyle("/upload")}>
          Upload
        </Link>

        <Link to="/ranking" className={linkStyle("/ranking")}>
          Ranking
        </Link>
      </div>
    </nav>
  );
}