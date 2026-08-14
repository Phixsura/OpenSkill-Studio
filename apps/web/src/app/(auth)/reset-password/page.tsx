"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, ApiError } from "@/lib/api";

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  if (!token) {
    return (
      <>
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight">Invalid link</h1>
          <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
            This password reset link is invalid or has expired.
          </p>
        </div>
        <Link
          href="/forgot-password"
          className="block text-center text-sm font-medium hover:underline"
        >
          Request a new reset link
        </Link>
      </>
    );
  }

  if (success) {
    return (
      <>
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight">Password reset</h1>
          <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
            Your password has been reset successfully.
          </p>
        </div>
        <Link href="/login">
          <Button className="w-full">Log in</Button>
        </Link>
      </>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

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
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await api("/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({ token, new_password: password }),
      });
      setSuccess(true);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Failed to reset password. The link may have expired.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight">Set new password</h1>
        <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
          Enter your new password below.
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="password" className="block text-sm font-medium">
            New password
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

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium">
            Confirm password
          </label>
          <Input
            id="confirmPassword"
            type="password"
            required
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="mt-1"
          />
        </div>

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Resetting..." : "Reset password"}
        </Button>
      </form>
    </>
  );
}
