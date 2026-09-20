"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";

/* ── Types ────────────────────────────────────────────────── */

interface Snapshot {
  id: string;
  user_id: string;
  share_token: string;
  checksum: string;
  included_fields: string[];
  issued_at: string;
  expires_at: string | null;
  status: string;
}

/* ── Constants ────────────────────────────────────────────── */

const SHAREABLE_FIELDS = [
  { value: "capabilities", label: "Capabilities" },
  { value: "credentials", label: "Credentials" },
  { value: "projects", label: "Projects" },
  { value: "portfolio", label: "Portfolio" },
  { value: "availability", label: "Availability" },
  { value: "learning_paths", label: "Learning Paths" },
  { value: "workflow_competencies", label: "Workflow Competencies" },
  { value: "commercial_history", label: "Commercial History" },
  { value: "verifications", label: "Verifications" },
];

/* ── Page ─────────────────────────────────────────────────── */

export default function SnapshotsPage() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [selectedFields, setSelectedFields] = useState<string[]>(["capabilities", "credentials"]);
  const [copied, setCopied] = useState<string | null>(null);

  const { data: snapshotsData, isLoading, isError } = useQuery({
    queryKey: ["passport-snapshots"],
    queryFn: () => apiWithAuth<{ data: Snapshot[] }>("/talent/passport/snapshots"),
  });

  const createSnapshot = useMutation({
    mutationFn: (body: { included_fields: string[] }) =>
      apiWithAuth<{ data: Snapshot }>("/talent/passport/snapshots", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["passport-snapshots"] });
      toast.success("Snapshot created");
      setShowCreate(false);
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Failed to create snapshot"),
  });

  const revokeSnapshot = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`/talent/passport/snapshots/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["passport-snapshots"] });
      toast.success("Snapshot revoked");
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Failed to revoke snapshot"),
  });

  const snapshots = snapshotsData?.data ?? [];
  const activeSnapshots = snapshots.filter((s) => s.status === "active");
  const revokedSnapshots = snapshots.filter((s) => s.status === "revoked");

  const toggleField = (field: string) => {
    setSelectedFields((prev) =>
      prev.includes(field) ? prev.filter((f) => f !== field) : [...prev, field],
    );
  };

  const copyShareLink = (token: string) => {
    const url = `${window.location.origin}/verify/passport/${token}`;
    navigator.clipboard.writeText(url).then(() => {
      setCopied(token);
      toast.success("Share link copied");
      setTimeout(() => setCopied(null), 2000);
    });
  };

  if (isError) return <div className="p-8 text-center text-red-600">Failed to load data</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Share Snapshots</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            Create tamper-proof, verifiable snapshots of your passport to share with employers.
          </p>
        </div>
        <Button onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? "Cancel" : "New Snapshot"}
        </Button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-5 shadow-sm">
          <h2 className="text-lg font-semibold">Create Snapshot</h2>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            Choose which fields to include. The snapshot is frozen at this moment — future changes
            won&apos;t update it.
          </p>

          <div className="mt-4 grid gap-2 sm:grid-cols-3">
            {SHAREABLE_FIELDS.map((field) => (
              <label
                key={field.value}
                className={cn(
                  "flex cursor-pointer items-center gap-2 rounded-md border px-3 py-2 text-sm transition-colors",
                  selectedFields.includes(field.value)
                    ? "border-[hsl(var(--primary))] bg-[hsl(var(--primary)/0.05)]"
                    : "hover:bg-[hsl(var(--secondary))]",
                )}
              >
                <input
                  type="checkbox"
                  checked={selectedFields.includes(field.value)}
                  onChange={() => toggleField(field.value)}
                />
                {field.label}
              </label>
            ))}
          </div>

          <div className="mt-4 flex justify-end">
            <Button
              onClick={() => createSnapshot.mutate({ included_fields: selectedFields })}
              disabled={createSnapshot.isPending || selectedFields.length === 0}
            >
              {createSnapshot.isPending ? "Creating…" : "Create Snapshot"}
            </Button>
          </div>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-[hsl(var(--primary))] border-t-transparent" />
        </div>
      )}

      {/* Active Snapshots */}
      {activeSnapshots.length === 0 && !isLoading && (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-[hsl(var(--muted-foreground))]">
          <p className="mb-2 text-lg font-medium">No active snapshots</p>
          <p>
            Create a snapshot to generate a verifiable share link. Employers can verify your
            capabilities without accessing your full passport.
          </p>
        </div>
      )}

      {activeSnapshots.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold">Active Snapshots</h2>
          <div className="space-y-2">
            {activeSnapshots.map((snap) => (
              <div
                key={snap.id}
                className="flex flex-col gap-3 rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium">
                    Created {new Date(snap.issued_at).toLocaleDateString()}{" "}
                    {new Date(snap.issued_at).toLocaleTimeString()}
                  </p>
                  <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
                    Fields: {snap.included_fields.join(", ")}
                  </p>
                  {snap.expires_at && (
                    <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
                      Expires {new Date(snap.expires_at).toLocaleDateString()}
                    </p>
                  )}
                  <p className="mt-1 font-mono text-xs text-[hsl(var(--muted-foreground))]">
                    SHA-256: {snap.checksum.slice(0, 16)}…
                  </p>
                </div>
                <div className="flex shrink-0 gap-2">
                  <Button variant="secondary" onClick={() => copyShareLink(snap.share_token)}>
                    {copied === snap.share_token ? "Copied!" : "Copy Link"}
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => revokeSnapshot.mutate(snap.id)}
                    disabled={revokeSnapshot.isPending}
                  >
                    Revoke
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Revoked Snapshots */}
      {revokedSnapshots.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold text-[hsl(var(--muted-foreground))]">
            Revoked Snapshots
          </h2>
          <div className="space-y-2">
            {revokedSnapshots.map((snap) => (
              <div
                key={snap.id}
                className="flex items-center justify-between rounded-lg border border-dashed p-4 opacity-60"
              >
                <div>
                  <p className="text-sm">Created {new Date(snap.issued_at).toLocaleDateString()}</p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Fields: {snap.included_fields.join(", ")}
                  </p>
                </div>
                <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900 dark:text-red-300">
                  Revoked
                </span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
