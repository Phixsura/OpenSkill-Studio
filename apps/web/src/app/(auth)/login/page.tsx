"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, ApiError } from "@/lib/api";
import { type AuthUser, useAuthStore } from "@/stores/auth";

interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

// Open-redirect guard: relative path only. Browsers treat "\" as "/" in
// URLs, so "/\evil.com" (or any backslash) must be rejected — and the
// WHATWG URL parser strips tab/newline/CR before parsing, so "/%09/evil.com"
// (decoded: "/\t/evil.com") would resolve external too. Strip those exactly
// like the parser does BEFORE applying the shape checks.
function safeRedirect(target: string | null): string {
  if (!target) return "/dashboard";
  const t = target.replace(/[\t\n\r]/g, "");
  if (!t.startsWith("/") || t.startsWith("//") || t.includes("\\")) {
    return "/dashboard";
  }
  return t;
}

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const setAuth = useAuthStore((s) => s.setAuth);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  // Redirect to dashboard if already logged in
  useEffect(() => {
    if (isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, router]);

  const verified = searchParams.get("verified") === "true";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await api<AuthResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
        credentials: "include",
      });
      setAuth(data.access_token, data.user);
      router.push(safeRedirect(searchParams.get("redirect")));
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Login failed. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight">Welcome back</h1>
        <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
          Log in to your account
        </p>
      </div>

      {verified && (
        <div className="rounded-md bg-green-50 p-3 text-sm text-green-700 dark:bg-green-950 dark:text-green-300">
          Email verified successfully! You can now log in.
        </div>
      )}

      {error && (
        <div role="alert" className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium">
            Email
          </label>
          <Input
            id="email"
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1"
          />
        </div>

        <div>
          <div className="flex items-center justify-between">
            <label htmlFor="password" className="block text-sm font-medium">
              Password
            </label>
            <Link
              href="/forgot-password"
              className="text-xs text-[hsl(var(--muted-foreground))] hover:underline"
            >
              Forgot password?
            </Link>
          </div>
          <Input
            id="password"
            type="password"
            required
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1"
          />
        </div>

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Logging in..." : "Log in"}
        </Button>
      </form>

      <p className="text-center text-sm text-[hsl(var(--muted-foreground))]">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="font-medium hover:underline">
          Sign up
        </Link>
      </p>
    </>
  );
}
