import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const handleLogout = () => {
    logout();
    navigate("/login");
  };
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span>⚡ EV Analytics</span>
        <small>cloud + ML demo</small>
      </div>
      <div className="navbar-links">
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/sessions">Sessions</NavLink>
        <NavLink to="/analytics">Analytics</NavLink>
        <NavLink to="/ml">ML Training</NavLink>
        <NavLink to="/predict">Predict</NavLink>
        <NavLink to="/jobs">Jobs</NavLink>
      </div>
      <div className="navbar-user">
        <span>{user?.email}</span>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  );
}
