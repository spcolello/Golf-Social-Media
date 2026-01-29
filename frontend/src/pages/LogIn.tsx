import { useState } from "react";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [output, setOutput] = useState("");

  const handleLogin = async () => {
    if (!username || !password) {
      setOutput("Username and Password Required");
      return;
    }

    try {
      const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setOutput("Error: " + (data.detail || "Login failed"));
        return;
      }
    
      localStorage.setItem("token", data.access_token)

    navigate("/feed");

    } catch (err) {
      if (err instanceof Error) setOutput("Error: " + err.message);
    }
  };

  return (
    <div>
      <h2>Log In</h2>

      <input
        placeholder="username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      <input
        type="password"
        placeholder="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button onClick={handleLogin}>Log In</button>
      <button onClick={() => navigate("/create-account")}>Create Account</button>

      <pre>{output}</pre>
    </div>
  );
};

export default LoginPage;
