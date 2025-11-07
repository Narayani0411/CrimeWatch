import { Link } from "react-router-dom";
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

const SignInPage = () => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="flex justify-center items-center min-h-screen fade-in">
      <div className="card max-w-md w-full text-left">
        <h1 className="text-3xl font-bold mb-2 text-indigo-600">Welcome Back</h1>
        <p className="text-gray-500 mb-6">
          Sign in to access your smart security dashboard.
        </p>

        <form className="space-y-5">
          <div>
            <label className="block mb-2 font-medium">Email Address</label>
            <input type="email" placeholder="you@example.com" required />
          </div>

          <div>
            <label className="block mb-2 font-medium">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-3 text-gray-500 hover:text-gray-700 transition"
              >
                {showPassword ? (
                  <EyeOff size={20} strokeWidth={2} />
                ) : (
                  <Eye size={20} strokeWidth={2} />
                )}
              </button>
            </div>
          </div>

          <button type="submit" className="btn w-full mt-4 text-base">
            🔑 Sign In
          </button>
        </form>

        <p className="text-center text-gray-500 mt-6">
          Don’t have an account?{" "}
          <Link to="/signup" className="text-indigo-500 hover:underline font-medium">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
};

export default SignInPage;
