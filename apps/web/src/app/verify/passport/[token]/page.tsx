"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface SnapshotVerification {
  status: string;
  payload?: {
    user_id: string;
    snapshot_at: string;
    capabilities?: {
      capability_id: string;
      capability_name: string;
      level: number;
      level_label: string;
      score: number;
      confidence: number;
      evidence_count: number;
    }[];
    [key: string]: unknown;
  };
  checksum?: string;
  issued_at?: string;
  expires_at?: string;
  revoked?: boolean;
  expired?: boolean;
}

const LEVEL_COLORS: Record<number, string> = {
  0: "bg-gray-100 text-gray-600",
  1: "bg-blue-100 text-blue-700",
  2: "bg-green-100 text-green-700",
  3: "bg-yellow-100 text-yellow-800",
  4: "bg-orange-100 text-orange-700",
  5: "bg-purple-100 text-purple-700",
};

export default function VerifyPassportPage() {
  const { token } = useParams<{ token: string }>();

  const { data, isLoading, error } = useQuery({
    queryKey: ["verify-passport", token],
    queryFn: () => api<{ data: SnapshotVerification }>(`/verify/passport/${token}`),
    enabled: !!token,
    retry: false,
  });

  const snapshot = data?.data;

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--background))]">
        <div className="text-[hsl(var(--muted-foreground))]">Verifying passport…</div>
      </div>
    );
  }

  if (error || !snapshot) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--background))]">
        <div className="mx-4 max-w-md rounded-lg border bg-[hsl(var(--card))] p-8 text-center shadow-sm">
          <div className="mb-4 text-4xl">🚫</div>
          <h1 className="mb-2 text-xl font-bold">Passport Not Found</h1>
          <p className="text-[hsl(var(--muted-foreground))]">
            This passport link may have expired, been revoked, or does not exist.
          </p>
        </div>
      </div>
    );
  }

  if (snapshot.revoked) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--background))]">
        <div className="mx-4 max-w-md rounded-lg border bg-[hsl(var(--card))] p-8 text-center shadow-sm">
          <div className="mb-4 text-4xl">🔒</div>
          <h1 className="mb-2 text-xl font-bold">Passport Revoked</h1>
          <p className="text-[hsl(var(--muted-foreground))]">
            The owner has revoked access to this passport snapshot.
          </p>
        </div>
      </div>
    );
  }

  if (snapshot.expired) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--background))]">
        <div className="mx-4 max-w-md rounded-lg border bg-[hsl(var(--card))] p-8 text-center shadow-sm">
          <div className="mb-4 text-4xl">⏰</div>
          <h1 className="mb-2 text-xl font-bold">Passport Expired</h1>
          <p className="text-[hsl(var(--muted-foreground))]">
            This passport snapshot has expired. Ask the owner for a new share link.
          </p>
        </div>
      </div>
    );
  }

  const payload = snapshot.payload;
  const capabilities = payload?.capabilities ?? [];

  return (
    <div className="min-h-screen bg-[hsl(var(--background))]">
      {/* Header */}
      <div className="border-b bg-[hsl(var(--card))]">
        <div className="mx-auto max-w-4xl px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Verified Skill Passport</h1>
              <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                OpenSkill Studio — Verified Snapshot
              </p>
            </div>
            <div className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
              ✓ Verified
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-4xl px-4 py-8">
        {/* Snapshot metadata */}
        <div className="mb-8 rounded-lg border bg-[hsl(var(--card))] p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold">Snapshot Details</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">Issued</p>
              <p className="font-medium">
                {snapshot.issued_at
                  ? new Date(snapshot.issued_at).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })
                  : "—"}
              </p>
            </div>
            {snapshot.expires_at && (
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Expires</p>
                <p className="font-medium">
                  {new Date(snapshot.expires_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
              </div>
            )}
            {snapshot.checksum && (
              <div className="sm:col-span-2">
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  Integrity Checksum (SHA-256)
                </p>
                <p className="mt-1 break-all rounded bg-[hsl(var(--secondary))] px-3 py-2 font-mono text-xs">
                  {snapshot.checksum}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Capabilities */}
        {capabilities.length > 0 && (
          <div className="mb-8">
            <h2 className="mb-4 text-lg font-semibold">Verified Capabilities</h2>
            <div className="grid gap-4 sm:grid-cols-2">
              {capabilities.map((cap) => (
                <div
                  key={cap.capability_id}
                  className="rounded-lg border bg-[hsl(var(--card))] p-5 shadow-sm"
                >
                  <div className="mb-3 flex items-start justify-between">
                    <h3 className="font-medium">{cap.capability_name}</h3>
                    <span
                      className={cn(
                        "rounded-full px-2.5 py-0.5 text-xs font-semibold",
                        LEVEL_COLORS[cap.level] ?? LEVEL_COLORS[0],
                      )}
                    >
                      L{cap.level}
                    </span>
                  </div>

                  <p className="mb-2 text-sm text-[hsl(var(--muted-foreground))]">
                    {cap.level_label}
                  </p>

                  {/* Score bar */}
                  <div className="mb-2">
                    <div className="flex justify-between text-xs text-[hsl(var(--muted-foreground))]">
                      <span>Score</span>
                      <span>{Math.round(cap.score * 100)}%</span>
                    </div>
                    <div className="mt-1 h-2 overflow-hidden rounded-full bg-[hsl(var(--secondary))]">
                      <div
                        className="h-full rounded-full bg-[hsl(var(--primary))]"
                        style={{ width: `${Math.round(cap.score * 100)}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex justify-between text-xs text-[hsl(var(--muted-foreground))]">
                    <span>{cap.evidence_count} evidence items</span>
                    <span>Confidence: {Math.round(cap.confidence * 100)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {capabilities.length === 0 && (
          <div className="mb-8 rounded-lg border bg-[hsl(var(--card))] p-8 text-center">
            <p className="text-[hsl(var(--muted-foreground))]">
              This snapshot does not include capability data.
            </p>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-[hsl(var(--muted-foreground))]">
          <p>
            This is a verified snapshot from <span className="font-medium">OpenSkill Studio</span>.
            The data shown was frozen at the time of issuance and cannot be altered.
          </p>
          <p className="mt-2">
            To verify integrity, compute SHA-256 of the payload JSON and compare with the checksum
            above.
          </p>
        </div>
      </div>
    </div>
  );
}
