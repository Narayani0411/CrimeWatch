import React, { useState } from 'react';

const AuthForm = ({ type }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const isSignUp = type === 'signup';

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(`${isSignUp ? 'Sign Up' : 'Sign In'} Attempt:`, { email, password });
    alert(`${isSignUp ? 'Sign Up' : 'Sign In'} successful (mock)!`);
    // In a real app, you'd call an API here and redirect the user.
  };

  const title = isSignUp ? 'Create an Account' : 'Sign In to Dashboard';
  const buttonText = isSignUp ? 'Sign Up' : 'Sign In';

  return (
    <form onSubmit={handleSubmit} className="p-8 bg-white rounded-xl shadow-2xl space-y-6 w-96">
      <h2 className="text-3xl font-bold text-center text-gray-800">{title}</h2>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
        className="w-full p-3 border border-gray-300 rounded-md"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(p.target.value)}
        placeholder="Password"
        required
        className="w-full p-3 border border-gray-300 rounded-md"
      />
      <button
        type="submit"
        className="w-full bg-indigo-600 text-white py-3 rounded-md font-semibold hover:bg-indigo-700 transition"
      >
        {buttonText}
      </button>
    </form>
  );
};

export default AuthForm;