import AuthForm from '../components/AuthForm';
import { Link } from 'react-router-dom';

const SignInPage = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] space-y-6">
      <h1 className="text-4xl font-bold text-indigo-700">Welcome Back 👋</h1>
      <AuthForm type="signin" />
      <p className="text-gray-600">
        Don't have an account?{' '}
        <Link to="/signup" className="text-indigo-600 hover:underline font-medium">
          Sign Up here
        </Link>
      </p>
    </div>
  );
};

export default SignInPage;