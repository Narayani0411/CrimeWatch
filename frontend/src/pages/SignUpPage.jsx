import AuthForm from '../components/AuthForm';
import { Link } from 'react-router-dom';

const SignUpPage = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] space-y-6">
      <h1 className="text-4xl font-bold text-green-700">Create Your Account 📝</h1>
      <AuthForm type="signup" />
      <p className="text-gray-600">
        Already have an account?{' '}
        <Link to="/signin" className="text-green-600 hover:underline font-medium">
          Sign In
        </Link>
      </p>
    </div>
  );
};

export default SignUpPage;