import { NavLink } from "react-router-dom";

export default function Navbar() {
  const linkStyle = ({ isActive }: { isActive: boolean }) => ({
    textDecoration: "none",
    fontWeight: isActive ? 700 : 400,
  });

  return (
    <nav style={{ display: "flex", gap: 12, padding: 12 }}>
      <NavLink to="/" style={linkStyle}>
        Feed
      </NavLink>
      <NavLink to="/account" style={linkStyle}>
        Account
      </NavLink>
      <NavLink to="/login" style={linkStyle}>
        Log In
      </NavLink>
    </nav>
  );
}