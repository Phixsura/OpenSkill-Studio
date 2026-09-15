"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

/* ── Types ────────────────────────────────────────────────── */

interface PassportData {
  user_id: string;
  default_visibility: string;
  discoverable: boolean;
  availability_status: string | null;
  availability_note: string | null;
  preferred_opportunity_types: string[];
  visible_fields: string[];
  capabilities: CapabilityScore[] | null;
}

interface CapabilityScore {
  capability_id: string;
  capability_name: string;
  level: number;
  level_label: string;
  score: number;
  depth?: number;
  breadth?: number;
  recency?: number;
  velocity?: number;
  confidence: number;
  evidence_count: number;
  substantial_evidence_count: number;
  last_verified_at: string | null;
  verification_mix: Record<string, number>;
  scoring_version: string;
  computed_at: string;
}

interface Credential {
  id: string;
  credential_type: string;
  version: number;
  status: string;
  issued_at: string;
  expires_at: string | null;
  capabilities: { capability_id: string; required_level: number; achieved_level: number }[];
}

interface EvidenceItem {
  id: string;
  capability_id: string;
  source_type: string;
  source_id: string;
  score_normalized: number | null;
  verification_level: string;
  occurred_at: string;
  status: string;
}

/* ── Constants ────────────────────────────────────────────── */

const LEVEL_COLORS: Record<number, string> = {
  0: "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
  1: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  2: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  3: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  4: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  5: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
};

const VERIFICATION_DOTS: Record<string, string> = {
  employer_verified: "bg-green-500",
  client_verified: "bg-emerald-500",
  assessment_verified: "bg-teal-500",
  instructor_verified: "bg-blue-500",
  peer_verified: "bg-yellow-500",
  system_observed: "bg-indigo-400",
  self_reported: "bg-gray-400",
};

const VERIFICATION_LABELS: Record<string, string> = {
  employer_verified: "Employer",
  client_verified: "Client",
  assessment_verified: "Assessment",
  instructor_verified: "Instructor",
  peer_verified: "Peer",
  system_observed: "System",
  self_reported: "Self",
};

const VISIBILITY_OPTIONS = [
  { value: "private", label: "Private", desc: "Only you can see" },
  { value: "organization_only", label: "Organization", desc: "Visible to your org members" },
  { value: "share_link", label: "Share Link", desc: "Anyone with a share link" },
  { value: "public_subset", label: "Public Subset", desc: "Selected fields visible publicly" },
];

const AVAILABILITY_OPTIONS = [
  { value: "", label: "Not set" },
  { value: "open", label: "Open to opportunities" },
  { value: "open_to_offers", label: "Open to offers" },
  { value: "not_looking", label: "Not looking" },
];

/* ── Radar Chart ─────────────────────────────────────────── */

function SkillRadarChart({ capabilities }: { capabilities: CapabilityScore[] }) {
  const items = capabilities.slice(0, 8);
  if (items.length < 3) return null;

  const size = 280;
  const cx = size / 2;
  const cy = size / 2;
  const radius = size * 0.36;
  const labelRadius = radius + 24;
  const n = items.length;

  const angleFor = (i: number) => (2 * Math.PI * i) / n - Math.PI / 2;

  const gridLevels = [0.2, 0.4, 0.6, 0.8, 1.0];

  const scorePoints = items
    .map((cap, i) => {
      const a = angleFor(i);
      const r = radius * Math.min(cap.score, 1);
      return `${cx + r * Math.cos(a)},${cy + r * Math.sin(a)}`;
    })
    .join(" ");

  // Truncate labels to fit
  const truncate = (s: string, max: number) => (s.length > max ? s.slice(0, max - 1) + "…" : s);

  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-5 shadow-sm">
      <h2 className="mb-3 text-lg font-semibold">Skill Profile</h2>
      <div className="flex justify-center">
        <svg
          viewBox={`0 0 ${size} ${size}`}
          className="h-auto w-full max-w-[320px]"
          role="img"
          aria-label="Skill radar chart"
        >
          {/* Grid rings */}
          {gridLevels.map((level) => {
            const pts = Array.from({ length: n }, (_, i) => {
              const a = angleFor(i);
              const r = radius * level;
              return `${cx + r * Math.cos(a)},${cy + r * Math.sin(a)}`;
            }).join(" ");
            return (
              <polygon
                key={level}
                points={pts}
                fill="none"
                stroke="currentColor"
                className="text-[hsl(var(--border))]"
                strokeWidth={level === 1.0 ? 1.5 : 0.5}
              />
            );
          })}

          {/* Axis lines */}
          {items.map((_, i) => {
            const a = angleFor(i);
            return (
              <line
                key={i}
                x1={cx}
                y1={cy}
                x2={cx + radius * Math.cos(a)}
                y2={cy + radius * Math.sin(a)}
                stroke="currentColor"
                className="text-[hsl(var(--border))]"
                strokeWidth={0.5}
              />
            );
          })}

          {/* Score polygon */}
          <polygon
            points={scorePoints}
            className="fill-[hsl(var(--primary)/0.2)] stroke-[hsl(var(--primary))]"
            strokeWidth={2}
          />

          {/* Score dots */}
          {items.map((cap, i) => {
            const a = angleFor(i);
            const r = radius * Math.min(cap.score, 1);
            return (
              <circle
                key={i}
                cx={cx + r * Math.cos(a)}
                cy={cy + r * Math.sin(a)}
                r={3}
                className="fill-[hsl(var(--primary))]"
              />
            );
          })}

          {/* Labels */}
          {items.map((cap, i) => {
            const a = angleFor(i);
            const lx = cx + labelRadius * Math.cos(a);
            const ly = cy + labelRadius * Math.sin(a);
            const cos = Math.cos(a);
            const anchor = Math.abs(cos) < 0.1 ? "middle" : cos > 0 ? "start" : "end";
            return (
              <text
                key={i}
                x={lx}
                y={ly}
                textAnchor={anchor}
                dominantBaseline="central"
                className="fill-[hsl(var(--foreground))] text-[9px]"
              >
                {truncate(cap.capability_name, 14)}
              </text>
            );
          })}
        </svg>
      </div>

      {/* Dimension breakdown (if multi-dimensional scoring) */}
      {items[0]?.depth !== undefined && (
        <div className="mt-4 grid grid-cols-4 gap-2 text-center text-xs">
          {(["depth", "breadth", "recency", "velocity"] as const).map((dim) => {
            const avg = items.reduce((s, c) => s + (c[dim] ?? 0), 0) / items.length;
            return (
              <div key={dim} className="rounded-md bg-[hsl(var(--secondary))] px-2 py-1.5">
                <p className="font-medium capitalize">{dim}</p>
                <p className="mt-0.5 tabular-nums text-[hsl(var(--muted-foreground))]">
                  {Math.round(avg * 100)}%
                </p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ── Page ─────────────────────────────────────────────────── */

export default function PassportPage() {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();

  const { data: passportData, isLoading: passportLoading } = useQuery({
    queryKey: ["passport"],
    queryFn: () => apiWithAuth<{ data: PassportData }>("/talent/passport"),
  });

  const { data: credentialsData } = useQuery({
    queryKey: ["credentials"],
    queryFn: () => apiWithAuth<{ data: Credential[] }>("/talent/credentials"),
  });

  const { data: evidenceData } = useQuery({
    queryKey: ["evidence"],
    queryFn: () =>
      apiWithAuth<{ data: EvidenceItem[]; meta: { total: number } }>(
        "/talent/evidence?per_page=20",
      ),
  });

  const updatePassport = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      apiWithAuth("/talent/passport", {
        method: "PATCH",
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["passport"] });
      toast.success("Passport updated");
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Failed to update passport"),
  });

  const passport = passportData?.data;
  const credentials = credentialsData?.data ?? [];
  const evidence = evidenceData?.data ?? [];
  const capabilities = passport?.capabilities ?? [];

  if (passportLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[hsl(var(--primary))] border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Skill Passport</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            Your verified talent identity — backed by real evidence.
          </p>
        </div>
        <Link href="/dashboard/passport/snapshots">
          <Button variant="secondary">Share Snapshots</Button>
        </Link>
      </div>

      {/* Settings Card */}
      <SettingsCard passport={passport} onUpdate={(body) => updatePassport.mutate(body)} />

      {/* Radar Chart */}
      {capabilities.length >= 3 && <SkillRadarChart capabilities={capabilities} />}

      {/* Capabilities Grid */}
      <section>
        <h2 className="mb-4 text-xl font-semibold">Capabilities</h2>
        {capabilities.length === 0 ? (
          <div className="rounded-lg border border-dashed p-12 text-center text-sm text-[hsl(var(--muted-foreground))]">
            <p className="mb-2 text-lg font-medium">No verified capabilities yet</p>
            <p>
              Complete skills, pass assessments, and work on projects to build your verified
              capability profile. Evidence is collected automatically as you progress.
            </p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {capabilities.map((cap) => (
              <CapabilityCard key={cap.capability_id} cap={cap} />
            ))}
          </div>
        )}
      </section>

      {/* Credentials */}
      <section>
        <h2 className="mb-4 text-xl font-semibold">Credentials</h2>
        {credentials.length === 0 ? (
          <div className="rounded-lg border border-dashed p-8 text-center text-sm text-[hsl(var(--muted-foreground))]">
            <p>No credentials yet. Pass standardized assessments to earn verified credentials.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {credentials.map((cred) => (
              <CredentialRow key={cred.id} cred={cred} />
            ))}
          </div>
        )}
      </section>

      {/* Evidence Timeline */}
      <section>
        <h2 className="mb-4 text-xl font-semibold">Recent Evidence</h2>
        {evidence.length === 0 ? (
          <div className="rounded-lg border border-dashed p-8 text-center text-sm text-[hsl(var(--muted-foreground))]">
            <p>No evidence recorded yet. Your learning and project activities will appear here.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {evidence.map((ev) => (
              <EvidenceRow key={ev.id} ev={ev} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

/* ── Settings Card ────────────────────────────────────────── */

function SettingsCard({
  passport,
  onUpdate,
}: {
  passport: PassportData | undefined;
  onUpdate: (body: Record<string, unknown>) => void;
}) {
  if (!passport) return null;

  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-5 shadow-sm">
      <h2 className="text-lg font-semibold">Passport Settings</h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {/* Visibility */}
        <div>
          <label className="mb-1 block text-sm font-medium">Visibility</label>
          <select
            value={passport.default_visibility}
            onChange={(e) => onUpdate({ default_visibility: e.target.value })}
            className="w-full rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
          >
            {VISIBILITY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label} — {opt.desc}
              </option>
            ))}
          </select>
        </div>

        {/* Discoverability */}
        <div>
          <label className="mb-1 block text-sm font-medium">Employer Discoverability</label>
          <label className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm">
            <input
              type="checkbox"
              checked={passport.discoverable}
              onChange={(e) => onUpdate({ discoverable: e.target.checked })}
            />
            <span>Allow employers to find me</span>
          </label>
          <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
            When enabled, your profile appears in employer talent searches.
          </p>
        </div>

        {/* Availability */}
        <div>
          <label className="mb-1 block text-sm font-medium">Availability</label>
          <select
            value={passport.availability_status ?? ""}
            onChange={(e) => onUpdate({ availability_status: e.target.value || null })}
            className="w-full rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
          >
            {AVAILABILITY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

/* ── Capability Card ──────────────────────────────────────── */

function CapabilityCard({ cap }: { cap: CapabilityScore }) {
  const scorePercent = Math.round(cap.score * 100);
  const verificationEntries = Object.entries(cap.verification_mix).filter(([, count]) => count > 0);

  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-sm font-semibold leading-tight">{cap.capability_name}</h3>
        <span
          className={cn(
            "shrink-0 rounded-full px-2 py-0.5 text-xs font-bold",
            LEVEL_COLORS[cap.level] ?? LEVEL_COLORS[0],
          )}
        >
          L{cap.level}
        </span>
      </div>

      <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">{cap.level_label}</p>

      {/* Score bar */}
      <div className="mt-3">
        <div className="flex items-center justify-between text-xs">
          <span className="font-medium">{scorePercent}%</span>
          <span className="text-[hsl(var(--muted-foreground))]">{cap.evidence_count} evidence</span>
        </div>
        <div className="mt-1 h-2 overflow-hidden rounded-full bg-[hsl(var(--secondary))]">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[hsl(var(--primary))] to-[hsl(var(--primary)/0.7)]"
            style={{ width: `${scorePercent}%` }}
          />
        </div>
      </div>

      {/* Multi-dimensional mini bars */}
      {cap.depth !== undefined && (
        <div className="mt-2 grid grid-cols-4 gap-1 text-[10px]">
          {(["depth", "breadth", "recency", "velocity"] as const).map((dim) => {
            const val = cap[dim] ?? 0;
            return (
              <div key={dim}>
                <span className="capitalize text-[hsl(var(--muted-foreground))]">
                  {dim.charAt(0).toUpperCase()}
                </span>
                <div className="mt-0.5 h-1 overflow-hidden rounded-full bg-[hsl(var(--secondary))]">
                  <div
                    className="h-full rounded-full bg-[hsl(var(--primary)/0.6)]"
                    style={{ width: `${Math.round(val * 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Verification mix */}
      {verificationEntries.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {verificationEntries.map(([level, count]) => (
            <span key={level} className="flex items-center gap-1 text-xs">
              <span
                className={cn(
                  "inline-block h-2 w-2 rounded-full",
                  VERIFICATION_DOTS[level] ?? "bg-gray-400",
                )}
              />
              <span className="text-[hsl(var(--muted-foreground))]">
                {VERIFICATION_LABELS[level] ?? level} ({count})
              </span>
            </span>
          ))}
        </div>
      )}

      {/* Last verified */}
      {cap.last_verified_at && (
        <p className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
          Last verified {new Date(cap.last_verified_at).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}

/* ── Credential Row ───────────────────────────────────────── */

function CredentialRow({ cred }: { cred: Credential }) {
  const statusColors: Record<string, string> = {
    active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    expired: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
    revoked: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
    superseded: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-200",
  };

  return (
    <div className="flex items-center justify-between rounded-lg border p-4">
      <div>
        <h3 className="text-sm font-semibold">
          {cred.credential_type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
        </h3>
        <p className="text-xs text-[hsl(var(--muted-foreground))]">
          Issued {new Date(cred.issued_at).toLocaleDateString()}
          {cred.expires_at && ` · Expires ${new Date(cred.expires_at).toLocaleDateString()}`}
        </p>
      </div>
      <span
        className={cn(
          "rounded-full px-2 py-0.5 text-xs font-medium capitalize",
          statusColors[cred.status] ?? statusColors.expired,
        )}
      >
        {cred.status}
      </span>
    </div>
  );
}

/* ── Evidence Row ─────────────────────────────────────────── */

function EvidenceRow({ ev }: { ev: EvidenceItem }) {
  return (
    <div className="flex items-center justify-between rounded-md border px-4 py-3">
      <div className="flex items-center gap-3">
        <span
          className={cn(
            "inline-block h-2.5 w-2.5 rounded-full",
            VERIFICATION_DOTS[ev.verification_level] ?? "bg-gray-400",
          )}
        />
        <div>
          <p className="text-sm font-medium">
            {ev.source_type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
          </p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">
            {VERIFICATION_LABELS[ev.verification_level] ?? ev.verification_level} ·{" "}
            {new Date(ev.occurred_at).toLocaleDateString()}
          </p>
        </div>
      </div>
      {ev.score_normalized != null && (
        <span className="font-mono text-sm">{Math.round(ev.score_normalized * 100)}%</span>
      )}
    </div>
  );
}
