import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface UserInfo {
  id: number;
  username: string;
  email: string | null;
  created_at: string;
}

export default function Account() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem("token");

      // Redirect to login if no token
      if (!token) {
        navigate("/login");
        return;
      }

      try {
        const res = await fetch("/me", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          credentials: "include",
        });

        if (!res.ok) {
          const errorData = await res.json();
          console.error("Error response:", errorData);
          setError("Failed to fetch user data: " + (errorData.detail || res.statusText));
          navigate("/login");
          return;
        }

        const data = await res.json();
        console.log("User data:", data);
        setUser(data);
      } catch (err) {
        if (err instanceof Error) {
          console.error("Fetch error:", err);
          setError(err.message);
        }
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!user) {
    return <div>No user data found</div>;
  }

  return (
    <div>
      <h1>Account</h1>
      <div>
        <p>
          <strong>Username:</strong> {user.username}
        </p>
        <p>
          <strong>Email:</strong> {user.email || "Not provided"}
        </p>
        <p>
          <strong>Member Since:</strong>{" "}
          {new Date(user.created_at).toLocaleDateString()}
        </p>
      </div>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}
