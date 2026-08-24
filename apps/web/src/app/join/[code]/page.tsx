"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

export default function JoinByCodePage() {
  const { code } = useParams<{ code: string }>();
  const router = useRouter();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  // Wait for auth hydration before showing the unauthenticated UI.
  // On hard refresh with a valid session cookie, AuthInitializer needs
  // a full network round-trip to restore the session; showing "log in"
  // during that gap misleads authenticated users.
  const [authChecked, setAuthChecked] = useState(false);
  useEffect(() => {
    // If already authenticated, we're done
    if (isAuthenticated) {
      setAuthChecked(true);
      return;
    }
    // Give the auth refresh a chance to complete (up to 2s)
    const timer = setTimeout(() => setAuthChecked(true), 2000);
    const unsub = useAuthStore.subscribe((state) => {
      if (state.isAuthenticated) {
        setAuthChecked(true);
        clearTimeout(timer);
      }
    });
    return () => {
      unsub();
      clearTimeout(timer);
    };
  }, [isAuthenticated]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!authChecked) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4">
        <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>
      </main>
    );
  }

  if (!isAuthenticated) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4">
        <h1 className="text-2xl font-bold">Join Organization</h1>
        <p className="text-[hsl(var(--muted-foreground))]">
          You need to log in or create an account first.
        </p>
        <div className="flex gap-3">
          <Link href={`/login?redirect=/join/${code}`}>
            <Button variant="secondary">Log in</Button>
          </Link>
          <Link href={`/register?redirect=/join/${code}`}>
            <Button>Sign up</Button>
          </Link>
        </div>
      </main>
    );
  }

  const handleJoin = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await apiWithAuth<{ data: { org_id: string } }>("/invites/join", {
        method: "POST",
        body: JSON.stringify({ code }),
      });
      setSuccess(true);
      setTimeout(() => router.push(`/dashboard/orgs/${res.data.org_id}`), 1500);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to join.");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4">
        <h1 className="text-2xl font-bold">🎉 Welcome!</h1>
        <p className="text-[hsl(var(--muted-foreground))]">
          You&apos;ve joined the organization. Redirecting...
        </p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-bold">Join Organization</h1>
      <p className="text-[hsl(var(--muted-foreground))]">
        You&apos;ve been invited to join an organization.
      </p>

      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      <Button onClick={handleJoin} disabled={loading}>
        {loading ? "Joining..." : "Accept & Join"}
      </Button>
    </main>
  );
}
