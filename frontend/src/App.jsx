import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useAuth } from "./context/AuthContext.jsx";
import HomePage from "./pages/HomePage";
import SignInPage from "./pages/SignInPage";
import SignUpPage from "./pages/SignUpPage";
import DashboardPage from "./pages/DashboardPage";
import AlertPage from "./pages/AlertPage";
import RegistrationPage from "./pages/RegistrationPage";
import ProtectedRoute from "./components/ProtectedRoute";
import "./app.css";

const AppContent = () => {
  const { isLoggedIn, logout } = useAuth();
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");
  const navigate = useNavigate(); // ✅ used for redirecting

  useEffect(() => {
    document.documentElement.className = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  // ✅ Handle logout and redirect
  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <>
      {/* Navbar */}
      <nav className="navbar flex justify-between items-center p-4 shadow-md sticky top-0 z-50 bg-white/90 dark:bg-gray-900/90 border-b border-purple-100 dark:border-gray-800 backdrop-blur-md">
        {/* Left Section - Links */}
        <div className="flex space-x-6 font-semibold">
          <Link to="/" className="nav-link hover:text-purple-600 transition-all">
            Home
          </Link>

          {isLoggedIn && (
            <>
              <Link to="/dashboard" className="nav-link hover:text-purple-600 transition-all">
                Dashboard
              </Link>
              <Link to="/alerts" className="nav-link hover:text-purple-600 transition-all">
                Alerts
              </Link>
              <Link to="/register" className="nav-link hover:text-purple-600 transition-all">
                Register
              </Link>
            </>
          )}
        </div>

        {/* Right Section - Theme + Auth Buttons */}
        <div className="flex items-center space-x-4">
          {/* Theme toggle */}
          <button
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            className="theme-btn px-4 py-2 rounded-lg font-medium transition-all duration-300 bg-purple-100 hover:bg-purple-200 text-gray-800 dark:bg-purple-800 dark:hover:bg-purple-700 dark:text-white"
          >
            {theme === "light" ? "🌙 Dark Mode" : "☀️ Light Mode"}
          </button>

          {/* Auth buttons */}
          {!isLoggedIn ? (
            <div className="flex space-x-3">
              <Link
                to="/signin"
                className="px-4 py-2 rounded-lg font-medium transition-all duration-300 bg-blue-100 hover:bg-blue-200 text-blue-700 dark:bg-blue-800 dark:hover:bg-blue-700 dark:text-white"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="px-4 py-2 rounded-lg font-medium transition-all duration-300 bg-green-100 hover:bg-green-200 text-green-700 dark:bg-green-800 dark:hover:bg-green-700 dark:text-white"
              >
                Sign Up
              </Link>
            </div>
          ) : (
            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded-lg font-medium transition-all duration-300 bg-red-100 hover:bg-red-200 text-red-700 dark:bg-red-800 dark:hover:bg-red-700 dark:text-white"
            >
              Sign Out
            </button>
          )}
        </div>
      </nav>

      {/* Main content */}
      <main className="content-container p-6 md:p-10 bg-transparent transition-all duration-500">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/signin" element={<SignInPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/alerts"
            element={
              <ProtectedRoute>
                <AlertPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/register"
            element={
              <ProtectedRoute>
                <RegistrationPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </>
  );
};

const App = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;
