"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const setAuth = useAuthStore((s) => s.setAuth);
  const accessToken = useAuthStore((s) => s.accessToken);

  const [displayName, setDisplayName] = useState(user?.display_name ?? "");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      const res = await apiWithAuth<{ data: typeof user }>("/auth/me", {
        method: "PUT",
        body: JSON.stringify({ display_name: displayName }),
      });
      if (res.data && accessToken) {
        setAuth(accessToken, res.data);
      }
      setMessage("Profile updated.");
    } catch (err) {
      setMessage(
        err instanceof ApiError ? err.message : "Failed to update profile.",
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Manage your account settings.
        </p>
      </div>

      <form onSubmit={handleSave} className="max-w-md space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium">
            Email
          </label>
          <Input
            id="email"
            type="email"
            value={user?.email ?? ""}
            disabled
            className="mt-1 opacity-60"
          />
        </div>

        <div>
          <label htmlFor="displayName" className="block text-sm font-medium">
            Display name
          </label>
          <Input
            id="displayName"
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            className="mt-1"
          />
        </div>

        {message && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">{message}</p>
        )}

        <Button type="submit" disabled={saving}>
          {saving ? "Saving..." : "Save changes"}
        </Button>
      </form>
    </div>
  );
}
