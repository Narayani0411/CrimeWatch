import React, { useState } from "react";

const RegistrationPage = () => {
  const [emails, setEmails] = useState({ email1: "", email2: "" });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="max-w-lg mx-auto card fade-in">
      <h1 className="text-3xl font-bold mb-4 text-blue-600 dark:text-blue-300">
        Register Alternate Emails 📧
      </h1>
      <p className="mb-6 opacity-80">
        Add up to two alternate email addresses for emergency alerts.
      </p>

      {submitted && (
        <div className="p-3 bg-green-100 border-l-4 border-green-500 rounded-md mb-4">
          ✅ Emails successfully registered!
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-semibold mb-1">
            Alternate Email 1 (Required)
          </label>
          <input
            type="email"
            required
            placeholder="primary@example.com"
            className="focus:ring focus:ring-blue-200"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold mb-1">
            Alternate Email 2 (Optional)
          </label>
          <input type="email" placeholder="secondary@example.com" />
        </div>
        <button type="submit" className="btn w-full">
          Save Emails
        </button>
      </form>
    </div>
  );
};

export default RegistrationPage;
