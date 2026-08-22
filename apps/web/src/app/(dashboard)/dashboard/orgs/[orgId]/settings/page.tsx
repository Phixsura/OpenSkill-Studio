"use client";

import { useParams } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface OrgDetail {
  id: string;
  name: string;
  description: string | null;
  role: string;
  settings: Record<string, unknown>;
}

export default function OrgSettingsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["org", orgId],
    queryFn: () => apiWithAuth<{ data: OrgDetail }>(`/orgs/${orgId}`),
  });

  const org = data?.data;
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [synced, setSynced] = useState(false);

  // Sync form when data first loads
  useEffect(() => {
    if (org && !synced) {
      setName(org.name);
      setDescription(org.description ?? "");
      setSynced(true);
    }
  }, [org, synced]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      await apiWithAuth(`/orgs/${orgId}`, {
        method: "PUT",
        body: JSON.stringify({ name, description: description || null }),
      });
      queryClient.invalidateQueries({ queryKey: ["org", orgId] });
      queryClient.invalidateQueries({ queryKey: ["my-orgs"] });
      setMessage({ type: "success", text: "Settings saved." });
    } catch (err) {
      setMessage({ type: "error", text: err instanceof ApiError ? err.message : "Failed to save." });
    } finally {
      setSaving(false);
    }
  };

  if (isLoading) return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  if (isError) return <p className="text-sm text-red-600">Failed to load settings. Please try again.</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Organization Settings</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Manage your organization details.
        </p>
      </div>

      <form onSubmit={handleSave} className="max-w-lg space-y-4">
        <div>
          <label htmlFor="orgName" className="block text-sm font-medium">
            Organization name
          </label>
          <Input
            id="orgName"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1"
          />
        </div>

        <div>
          <label htmlFor="orgDesc" className="block text-sm font-medium">
            Description
          </label>
          <textarea
            id="orgDesc"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          />
        </div>

        {message && (
          <p className={`text-sm ${message.type === "error" ? "text-red-600" : "text-green-600"}`}>{message.text}</p>
        )}

        <Button type="submit" disabled={saving || !name.trim()}>
          {saving ? "Saving..." : "Save changes"}
        </Button>
      </form>
    </div>
  );
}
