import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
  const navigate = useNavigate();
  const [isVerified, setIsVerified] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/signin");
      return;
    }

    fetch("http://localhost:8000/auth/verify", {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Invalid token");
        setIsVerified(true);
      })
      .catch(() => {
        localStorage.removeItem("token");
        navigate("/signin");
      });
  }, [navigate]);

  if (!isVerified)
    return <p className="text-center mt-10">🔒 Checking authentication...</p>;

  return children;
};

export default ProtectedRoute;
