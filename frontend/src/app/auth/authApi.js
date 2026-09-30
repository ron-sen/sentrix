const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    ...options,
    headers: {
      ...options.headers,
    },
  });

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : null;

  if (!response.ok) {
    throw new Error(data?.detail || data?.message || "Request failed. Please try again.");
  }

  return data;
}

export function loginUser({ email, password }) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  return request("/signin", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });
}

export function signupUser({ email, password }) {
  return request("/signup", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      mail: email,
      password,
    }),
  });
}

export function verifyEmail(token) {
  return request(`/verify?token=${encodeURIComponent(token)}`);
}

export function resendVerification() {
  throw new Error("Resend verification is not implemented in the backend yet.");
}

export function startOAuth() {
  throw new Error("OAuth is not implemented in the backend yet.");
}