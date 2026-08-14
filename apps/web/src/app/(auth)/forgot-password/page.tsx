"use client";

import Link from "next/link";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await api("/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setSubmitted(true);
    } catch {
      // Always show success — backend never reveals user existence
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <>
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight">Check your email</h1>
          <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
            If an account exists for <strong>{email}</strong>, we&apos;ve sent a
            password reset link.
          </p>
        </div>
        <Link
          href="/login"
          className="block text-center text-sm font-medium hover:underline"
        >
          ← Back to login
        </Link>
      </>
    );
  }

  return (
    <>
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight">Reset password</h1>
        <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
          Enter your email and we&apos;ll send a reset link.
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
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

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Sending..." : "Send reset link"}
        </Button>
      </form>

      <p className="text-center text-sm text-[hsl(var(--muted-foreground))]">
        Remember your password?{" "}
        <Link href="/login" className="font-medium hover:underline">
          Log in
        </Link>
      </p>
    </>
  );
}
