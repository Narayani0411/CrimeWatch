import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import HomePage from "./pages/HomePage";
import SignInPage from "./pages/SignInPage";
import SignUpPage from "./pages/SignUpPage";
import DashboardPage from "./pages/DashboardPage";
import AlertPage from "./pages/AlertPage";
import RegistrationPage from "./pages/RegistrationPage";
import "./app.css";

const App = () => {
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");

  useEffect(() => {
    document.documentElement.className = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <Router>
      {/* Navbar */}
      <nav className="navbar flex justify-between items-center p-4 shadow-md sticky top-0 z-50">
        <div className="flex space-x-6 font-semibold">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/dashboard" className="nav-link">Dashboard</Link>
          <Link to="/alerts" className="nav-link">Alerts</Link>
          <Link to="/register" className="nav-link">Register</Link>
        </div>

        <button
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          className="theme-btn px-4 py-2 rounded-lg font-medium transition-all duration-300"
        >
          {theme === "light" ? "🌙 Dark Mode" : "☀️ Light Mode"}
        </button>
      </nav>

      {/* Page Container */}
      <main className="content-container p-6 md:p-10">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/signin" element={<SignInPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/alerts" element={<AlertPage />} />
          <Route path="/register" element={<RegistrationPage />} />
        </Routes>
      </main>
    </Router>
  );
};

export default App;
