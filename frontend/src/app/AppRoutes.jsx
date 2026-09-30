import { Navigate, Route, Routes } from "react-router-dom";
import {
  AuthFormPage,
  PendingVerificationPage,
  VerifiedPage,
  VerifyEmailPage,
} from "./auth/AuthPage";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/auth/signin" replace />} />
      <Route path="/auth/signin" element={<AuthFormPage mode="signin" />} />
      <Route path="/auth/signup" element={<AuthFormPage mode="signup" />} />
      <Route path="/auth/pending-verification" element={<PendingVerificationPage />} />
      <Route path="/auth/verified" element={<VerifiedPage />} />
      <Route path="/auth/verify-email" element={<VerifyEmailPage />} />
      <Route path="/dashboard" element={<div>Logged in</div>} />
    </Routes>
  );
}
