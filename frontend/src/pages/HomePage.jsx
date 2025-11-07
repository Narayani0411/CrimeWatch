import { Link } from "react-router-dom";

const HomePage = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen fade-in text-center">
      <h1 className="text-5xl font-extrabold mb-8 tracking-tight">CrimeWatch</h1>
      <p className="text-lg text-gray-500 mb-12 max-w-md">
        Welcome to our smart security monitoring dashboard. Please sign in or sign up to continue.
      </p>

      <div className="flex flex-col sm:flex-row sm:space-x-8 space-y-4 sm:space-y-0">
        <Link to="/signin" className="btn text-lg shadow-lg">
          🔑 Sign In
        </Link>
        <Link to="/signup" className="btn text-lg shadow-lg">
          📝 Sign Up
        </Link>
      </div>
    </div>
  );
};

export default HomePage;
