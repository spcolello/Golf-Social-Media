import { useState } from "react";
import { useNavigate } from "react-router-dom";

const CreateUser = () => {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [output, setOutput] = useState("");

  const handleCreateUser = async () => {
    if (!username || !password) {
      setOutput("Error: Username and password are required");
      return;
    }

    try {
      const res = await fetch("/user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          password,
          email: email || null,
        }),
      });

      let data: any;
      try {
        data = await res.json();
      } catch {
        data = { detail: "Invalid response from server" };
      }

      if (!res.ok) {
        setOutput("Error: " + (data.detail || "Failed to create user"));
        return;
      }

      setOutput("Success! User created:\n\n" + JSON.stringify(data, null, 2));
      setUsername("");
      setPassword("");
      setEmail("");

      // Optional: send them back to login after success
      setTimeout(() => {
        navigate("/");
      }, 800);
    } catch (err) {
      if (err instanceof Error) setOutput("Error: " + err.message);
    }
  };

  return (
    <div>
      <h2>Create User</h2>

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

      <input
        placeholder="email (optional)"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <button onClick={handleCreateUser}>Create</button>
      <button onClick={() => navigate("/login")}>Log In</button>

      <pre>{output}</pre>
    </div>
  );
};

export default CreateUser;