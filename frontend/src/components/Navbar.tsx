import { Link, useNavigate } from "react-router-dom";
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
      <span className="navbar-brand">⚡ EV Analytics</span>
      <div className="navbar-links">
        <Link to="/">Dashboard</Link>
        <Link to="/sessions">Sessions</Link>
        <Link to="/analytics">Analytics</Link>
        <Link to="/ml">ML Training</Link>
        <Link to="/predict">Predict</Link>
        <Link to="/jobs">Jobs</Link>
      </div>
      <div className="navbar-user">
        <span>{user?.email}</span>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  );
}
