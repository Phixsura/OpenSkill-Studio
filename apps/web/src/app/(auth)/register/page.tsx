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

export default function RegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const setAuth = useAuthStore((s) => s.setAuth);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  // Redirect if already logged in (unless coming from invite)
  useEffect(() => {
    if (isAuthenticated && !searchParams.get("redirect")) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, router, searchParams]);

  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [registered, setRegistered] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Client-side password validation
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (!/[A-Z]/.test(password)) {
      setError("Password must contain at least one uppercase letter.");
      return;
    }
    if (!/\d/.test(password)) {
      setError("Password must contain at least one digit.");
      return;
    }

    setLoading(true);

    try {
      const data = await api<AuthResponse>("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email,
          password,
          display_name: displayName,
        }),
        credentials: "include",
      });
      setAuth(data.access_token, data.user);
      setRegistered(true);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Registration failed. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  if (registered) {
    return (
      <>
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight">Check your email</h1>
          <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
            We&apos;ve sent a verification link to <strong>{email}</strong>.
            Please verify your email to unlock all features.
          </p>
        </div>
        <Button onClick={() => {
          const redirect = searchParams.get("redirect") ?? "/dashboard";
          router.push(redirect.startsWith("/") && !redirect.startsWith("//") ? redirect : "/dashboard");
        }} className="w-full">
          Continue to Dashboard
        </Button>
      </>
    );
  }

  return (
    <>
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight">Create an account</h1>
        <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
          Join OpenSkill Studio
        </p>
      </div>

      {error && (
        <div role="alert" className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="displayName" className="block text-sm font-medium">
            Name
          </label>
          <Input
            id="displayName"
            type="text"
            required
            minLength={2}
            maxLength={100}
            autoComplete="name"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            className="mt-1"
          />
        </div>

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
          <label htmlFor="password" className="block text-sm font-medium">
            Password
          </label>
          <Input
            id="password"
            type="password"
            required
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1"
          />
          <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
            At least 8 characters, one uppercase letter, one digit.
          </p>
        </div>

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Creating account..." : "Sign up"}
        </Button>
      </form>

      <p className="text-center text-sm text-[hsl(var(--muted-foreground))]">
        Already have an account?{" "}
        <Link href="/login" className="font-medium hover:underline">
          Log in
        </Link>
      </p>
    </>
  );
}
