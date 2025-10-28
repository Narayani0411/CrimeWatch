import React, { useState } from 'react';

const RegistrationPage = () => {
  const [emails, setEmails] = useState({
    alternateEmail1: '',
    alternateEmail2: '',
  });
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleChange = (e) => {
    setEmails({
      ...emails,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real project, you would send these emails to a backend server.
    console.log('Alternate Emails Registered:', emails);
    setIsSubmitted(true);
    // Optionally clear the form after submission
    // setEmails({ alternateEmail1: '', alternateEmail2: '' }); 
  };

  return (
    <div className="max-w-xl mx-auto p-8 bg-white rounded-lg shadow-xl">
      <h1 className="text-3xl font-bold mb-6 text-blue-700">Register Alternate Emails 📧</h1>
      <p className="mb-6 text-gray-600">
        Register up to two additional email addresses to receive critical system alerts.
      </p>

      {isSubmitted && (
        <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
          Emails successfully registered!
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email Field 1 */}
        <div>
          <label htmlFor="email1" className="block text-sm font-medium text-gray-700">Alternate Email 1 (Required)</label>
          <input
            id="email1"
            type="email"
            name="Email"
            value={emails.alternateEmail1}
            onChange={handleChange}
            placeholder="primary-alert@example.com"
            required
            className="mt-1 w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        
        {/* Email Field 2 */}
        <div>
          <label htmlFor="email2" className="block text-sm font-medium text-gray-700">Alternate Email 2 (Optional)</label>
          <input
            id="email2"
            type="email"
            name="alternateEmail"
            value={emails.alternateEmail2}
            onChange={handleChange}
            placeholder="secondary-alert@example.com"
            className="mt-1 w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-3 rounded-md font-semibold hover:bg-blue-700 transition duration-200"
        >
          Save Alternate Emails
        </button>
      </form>
    </div>
  );
};

export default RegistrationPage;