import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import {
  loginUser,
  resendVerification,
  signupUser,
  startOAuth,
  verifyEmail,
} from "./authApi";
import "./auth.css";

const AUTH_COPY = {
  signin: {
    title: "Welcome Back !",
    subtitle: "Good to see u again, Enter your registered email and password.",
    submitLabel: "Login",
    footerText: "New here?",
    footerRoute: "/auth/signup",
    footerAction: "Create account",
  },
  signup: {
    title: "Getting Started",
    subtitle: "",
    submitLabel: "Create account",
    footerText: "Already an user ?",
    footerRoute: "/auth/signin",
    footerAction: "Sign in",
  },
};

function AppleIcon() {
  return (
    <svg className="apple-mark" viewBox="0 0 24 28" aria-hidden="true">
      <path d="M17.6 14.6c0-3.4 2.8-5 2.9-5.1-1.6-2.3-4-2.6-4.8-2.7-2-.2-4 1.2-5 1.2-1.1 0-2.7-1.2-4.4-1.1-2.3 0-4.4 1.3-5.6 3.4-2.4 4.1-.6 10.2 1.7 13.5 1.1 1.6 2.5 3.5 4.2 3.4 1.7-.1 2.3-1.1 4.4-1.1 2 0 2.6 1.1 4.4 1.1 1.8 0 3-1.7 4.1-3.3 1.3-1.9 1.8-3.7 1.8-3.8 0 0-3.6-1.4-3.7-5.5ZM14.4 4.6c.9-1.1 1.5-2.6 1.4-4.1-1.4.1-3 .9-4 2-.9 1-1.6 2.6-1.4 4 1.5.1 3.1-.8 4-1.9Z" />
    </svg>
  );
}

export function AuthFormPage({ mode }) {
  const navigate = useNavigate();
  const copy = AUTH_COPY[mode];
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function updateField(event) {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    const payload = {
      email: form.email.trim(),
      password: form.password,
    };

    if (!payload.email || !payload.password) {
      setError("Please enter your email and password.");
      return;
    }

    setIsSubmitting(true);

    try {
      if (mode === "signin") {
        const data = await loginUser(payload);
        navigate(data?.redirectTo || "/dashboard", { replace: true });
        return;
      }

      await signupUser(payload);
      navigate("/auth/pending-verification", {
        replace: true,
        state: { email: payload.email },
      });
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-panel" aria-labelledby="auth-title">
        <h1 className="auth-title" id="auth-title">
          {copy.title}
        </h1>
        {copy.subtitle ? <p className="auth-subtitle">{copy.subtitle}</p> : null}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <label className="field-group">
            <span className="field-label">Email</span>
            <input
              className="text-field"
              name="email"
              type="email"
              autoComplete="email"
              value={form.email}
              onChange={updateField}
              required
            />
          </label>

          <label className="field-group">
            <span className="field-label">Password</span>
            <input
              className="text-field"
              name="password"
              type="password"
              autoComplete={mode === "signin" ? "current-password" : "new-password"}
              value={form.password}
              onChange={updateField}
              minLength={6}
              required
            />
          </label>

          <div className="form-row">
            <Link className="small-link" to={copy.footerRoute}>
              {copy.footerText} {copy.footerAction}
            </Link>
          </div>

          <p className="status-message">{error}</p>

          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Please wait..." : copy.submitLabel}
          </button>
        </form>

        <div className="oauth-row" aria-label="Social sign in">
          <button
            className="oauth-button"
            type="button"
            onClick={() => startOAuth("google")}
            aria-label="Continue with Google"
          >
            <span className="google-mark">G</span>
          </button>

          <button
            className="oauth-button"
            type="button"
            onClick={() => startOAuth("apple")}
            aria-label="Continue with Apple"
          >
            <AppleIcon />
          </button>
        </div>
      </section>
    </main>
  );
}

export function PendingVerificationPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const email = location.state?.email || "";
  const [message, setMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  async function handleResend() {
    setMessage("");
    setIsSuccess(false);

    if (!email) {
      setMessage("Email is missing. Please sign up again.");
      return;
    }

    try {
      await resendVerification(email);
      setIsSuccess(true);
      setMessage("Verification link sent again.");
    } catch (caughtError) {
      setMessage(caughtError.message);
    }
  }

  return (
    <AuthNotice>
      <div className="notice">
        Verify your mail ! we have sent you a{" "}
        <strong className="danger">verification</strong> link on your mail .
      </div>
      <div className="notice-actions">
        <button className="small-link" type="button" onClick={handleResend}>
          Resend link
        </button>
        <button className="small-link" type="button" onClick={() => navigate("/auth/signin")}>
          Back to sign in
        </button>
      </div>
      <p className={`status-message ${isSuccess ? "success" : ""}`}>{message}</p>
    </AuthNotice>
  );
}

export function VerifiedPage() {
  return (
    <AuthNotice>
      <div className="notice">
        Your Email is <strong className="success">Verified !</strong>
      </div>
      <div className="notice-actions">
        <Link className="small-link" to="/auth/signin">
          Continue to sign in
        </Link>
      </div>
    </AuthNotice>
  );
}

export function VerifyEmailPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const token = useMemo(() => params.get("token"), [params]);

  useEffect(() => {
    async function runVerification() {
      if (!token) {
        navigate("/auth/pending-verification", { replace: true });
        return;
      }

      try {
        await verifyEmail(token);
        navigate("/auth/verified", { replace: true });
      } catch {
        navigate("/auth/pending-verification", { replace: true });
      }
    }

    runVerification();
  }, [navigate, token]);

  return (
    <AuthNotice>
      <div className="notice">Verifying your email...</div>
    </AuthNotice>
  );
}

function AuthNotice({ children }) {
  return (
    <main className="auth-shell">
      <section className="auth-panel is-notice">{children}</section>
    </main>
  );
}
