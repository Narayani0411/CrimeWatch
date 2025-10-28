import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import SignInPage from './pages/SignInPage'; 
import SignUpPage from './pages/SignUpPage'; 
import DashboardPage from './pages/DashboardPage';
import AlertPage from './pages/AlertPage';
import RegistrationPage from './pages/RegistrationPage';

const App = () => {
  return (
    <Router>
      {/* Updated Navbar: Removed Sign In/Sign Up links */}
      <nav className="p-4 bg-gray-800 text-white flex justify-between">
        <div className="flex space-x-4">
          <Link to="/" className="hover:text-blue-400 font-bold">Home</Link>
          <Link to="/dashboard" className="hover:text-blue-400">Dashboard</Link>
          <Link to="/alerts" className="hover:text-blue-400">Alerts</Link>
          <Link to="/register" className="hover:text-blue-400">Register Email</Link>
        </div>
        {/* The right side (which contained the Sign In/Sign Up buttons) is now empty */}
      </nav>

      <div className="p-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/signin" element={<SignInPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/alerts" element={<AlertPage />} />
          <Route path="/register" element={<RegistrationPage />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;