import { useState, FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import ErrorMessage from "../components/ErrorMessage";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, fullName);
      navigate("/");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <h1>Register</h1>
      <form onSubmit={handleSubmit} aria-label="register-form">
        <label htmlFor="fullName">Full name</label>
        <input id="fullName" value={fullName} onChange={(e) => setFullName(e.target.value)} />
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={email}
          onChange={(e) => setEmail(e.target.value)} required />
        <label htmlFor="password">Password</label>
        <input id="password" type="password" value={password}
          onChange={(e) => setPassword(e.target.value)} required minLength={6} />
        <ErrorMessage message={error} />
        <button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Register"}
        </button>
      </form>
      <p>Have an account? <Link to="/login">Login</Link></p>
    </div>
  );
}
