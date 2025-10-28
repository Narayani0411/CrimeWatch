import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    // The container uses min-h-screen to take up the full viewport height 
    // and flex classes to center content both horizontally (items-center) 
    // and vertically (justify-center).
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4">
      
      {/* Title */}
      <h1 className="text-5xl font-extrabold text-indigo-800 mb-10 text-center">
        Security System Access
      </h1>

      {/* Button Container */}
      <div className="flex flex-col space-y-6 sm:flex-row sm:space-x-8 sm:space-y-0">
        
        {/* Sign In Button */}
        <Link 
          to="/signin" 
          className="w-64 py-4 px-10 text-center bg-indigo-600 text-white text-xl font-semibold rounded-xl shadow-2xl transition duration-300 hover:bg-indigo-700 transform hover:scale-105"
        >
          🔑 Sign In
        </Link>
        
        {/* Sign Up Button */}
        <Link 
          to="/signup" 
          className="w-64 py-4 px-10 text-center border-4 border-indigo-600 text-indigo-600 text-xl font-semibold rounded-xl shadow-2xl transition duration-300 hover:bg-indigo-100 transform hover:scale-105"
        >
          📝 Sign Up
        </Link>
      </div>
    </div>
  );
};

export default HomePage;