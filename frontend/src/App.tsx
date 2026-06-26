import { Routes, Route } from "react-router-dom";
import { AuthProvider } from "./hooks/useAuth";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import SessionsPage from "./pages/SessionsPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import MLTrainingPage from "./pages/MLTrainingPage";
import PredictionPage from "./pages/PredictionPage";
import JobsPage from "./pages/JobsPage";

const protectedPage = (el: React.ReactNode) => (
  <ProtectedRoute>
    <Layout>{el}</Layout>
  </ProtectedRoute>
);

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={protectedPage(<DashboardPage />)} />
        <Route path="/sessions" element={protectedPage(<SessionsPage />)} />
        <Route path="/analytics" element={protectedPage(<AnalyticsPage />)} />
        <Route path="/ml" element={protectedPage(<MLTrainingPage />)} />
        <Route path="/predict" element={protectedPage(<PredictionPage />)} />
        <Route path="/jobs" element={protectedPage(<JobsPage />)} />
      </Routes>
    </AuthProvider>
  );
}
