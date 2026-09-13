"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, ApiError } from "@/lib/api";

interface GuestSession {
  access_token: string;
  token_type: string;
  project: { id: string; title: string };
  role: string;
  label: string;
  expires_in: number;
}

export default function ClientAccessPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api<{ data: GuestSession }>("/client-portal/guest-session", {
        method: "POST",
        body: JSON.stringify({ token, ...(email ? { email } : {}) }),
      });
      const session = res.data;
      // Session-scoped storage only: the guest JWT lives ≤30 min and dies
      // with the tab — never persisted to localStorage.
      sessionStorage.setItem("client_portal_jwt", session.access_token);
      sessionStorage.setItem("client_portal_role", session.role);
      sessionStorage.setItem("client_portal_label", session.label);
      router.push(`/client/${session.project.id}`);
    } catch (err) {
      // R101[L2]: 422 (malformed code / bad email shape) and 429 (rate
      // limited) collapsed into a generic message with no actionable detail.
      if (err instanceof ApiError && err.status === 401) {
        setError("This link is invalid or has expired. Ask your contact for a new one.");
      } else if (err instanceof ApiError && err.status === 429) {
        setError("Too many attempts — wait a minute and try again.");
      } else if (err instanceof ApiError && err.status === 422) {
        setError(err.message || "The access code or email looks malformed.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--secondary))] p-4">
      <div className="w-full max-w-md space-y-6 rounded-lg border bg-[hsl(var(--card))] p-8 shadow-sm">
        <div className="text-center">
          <h1 className="text-xl font-bold">Project review access</h1>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            Enter the access code you received to review project deliverables.
          </p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            placeholder="Access code"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            autoFocus
          />
          <Input
            type="email"
            placeholder="Your email (if the link is bound to one)"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" className="w-full" disabled={!token || loading}>
            {loading ? "Checking…" : "Open project"}
          </Button>
        </form>
      </div>
    </div>
  );
}
