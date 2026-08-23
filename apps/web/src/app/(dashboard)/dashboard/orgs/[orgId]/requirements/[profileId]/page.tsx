"use client";

// Review & confirm screen: every field carries a provenance badge
// (AI extracted vs human-entered). Extracted values never become hard
// constraints until edited or confirmed by a human (R14).

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Profile {
  id: string;
  context_type: string;
  raw_request: string | null;
  structured_requirements: Record<string, unknown>;
  extraction_meta: { provenance?: Record<string, string>; unmatched_mentions?: string[] } | null;
  status: string;
}

const EDITABLE_FIELDS: { key: string; label: string; kind: "text" | "number" | "list" }[] = [
  { key: "goal", label: "Goal", kind: "text" },
  { key: "scenario", label: "Scenario", kind: "text" },
  { key: "output_type", label: "Output type", kind: "text" },
  { key: "difficulty", label: "Current level", kind: "text" },
  { key: "time_budget", label: "Time budget (minutes)", kind: "number" },
  { key: "required_capabilities", label: "Required capabilities", kind: "list" },
  { key: "preferred_capabilities", label: "Preferred capabilities", kind: "list" },
  { key: "tool_constraints", label: "Tool constraints", kind: "list" },
];

function ProvenanceBadge({ source }: { source?: string }) {
  if (source === "extracted") {
    return (
      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-200">
        AI extracted
      </span>
    );
  }
  if (source === "user_entered") {
    return (
      <span className="rounded-full bg-green-100 px-2 py-0.5 text-[10px] font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
        You entered
      </span>
    );
  }
  return null;
}

export default function RequirementProfilePage() {
  const { orgId, profileId } = useParams<{ orgId: string; profileId: string }>();
  const queryClient = useQueryClient();
  const synced = useRef(false);
  const [fields, setFields] = useState<Record<string, string>>({});

  const { data, isLoading } = useQuery({
    queryKey: ["requirement-profile", orgId, profileId],
    queryFn: () =>
      apiWithAuth<{ data: Profile }>(`/orgs/${orgId}/requirement-profiles/${profileId}`),
  });
  const profile = data?.data;

  useEffect(() => {
    if (profile && !synced.current) {
      synced.current = true;
      const initial: Record<string, string> = {};
      for (const f of EDITABLE_FIELDS) {
        const v = profile.structured_requirements[f.key];
        if (v == null) initial[f.key] = "";
        else if (Array.isArray(v)) initial[f.key] = v.join(", ");
        else initial[f.key] = String(v);
      }
      setFields(initial);
    }
  }, [profile]);

  const saveMutation = useMutation({
    mutationFn: () => {
      const edits: Record<string, unknown> = {};
      for (const f of EDITABLE_FIELDS) {
        const raw = fields[f.key]?.trim() ?? "";
        const original = profile?.structured_requirements[f.key];
        const originalStr =
          original == null ? "" : Array.isArray(original) ? original.join(", ") : String(original);
        if (raw === originalStr) continue; // unchanged
        if (!raw) {
          edits[f.key] = null;
        } else if (f.kind === "number") {
          edits[f.key] = parseInt(raw, 10);
        } else if (f.kind === "list") {
          edits[f.key] = raw.split(",").map((s) => s.trim()).filter(Boolean);
        } else {
          edits[f.key] = raw;
        }
      }
      return apiWithAuth(`/orgs/${orgId}/requirement-profiles/${profileId}`, {
        method: "PATCH",
        body: JSON.stringify({ edits }),
      });
    },
    onSuccess: () => {
      toast.success("Profile updated");
      queryClient.invalidateQueries({ queryKey: ["requirement-profile", orgId, profileId] });
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Failed to save"),
  });

  const confirmMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/requirement-profiles/${profileId}/confirm`, {
        method: "POST",
      }),
    onSuccess: () => {
      toast.success("Profile confirmed");
      queryClient.invalidateQueries({ queryKey: ["requirement-profile", orgId, profileId] });
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Failed to confirm"),
  });

  if (isLoading || !profile) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }

  const provenance = profile.extraction_meta?.provenance ?? {};
  const unmatched = profile.extraction_meta?.unmatched_mentions ?? [];
  const confirmed = profile.status === "confirmed";

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Requirement Profile</h1>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            {profile.context_type.replace("_", " ")} ·{" "}
            {confirmed ? "Confirmed" : "Draft — review and confirm"}
          </p>
        </div>
        {confirmed && (
          <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
            Confirmed
          </span>
        )}
      </div>

      {unmatched.length > 0 && (
        <div className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-xs text-amber-800 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200">
          Unrecognized mentions (not mapped to any known value):{" "}
          {unmatched.join(", ")}
        </div>
      )}

      <div className="space-y-4 rounded-lg border p-4">
        {EDITABLE_FIELDS.map((f) => (
          <div key={f.key} className="space-y-1.5">
            <div className="flex items-center gap-2">
              <label htmlFor={`field-${f.key}`} className="text-sm font-medium">
                {f.label}
              </label>
              <ProvenanceBadge source={provenance[f.key]} />
            </div>
            <Input
              id={`field-${f.key}`}
              value={fields[f.key] ?? ""}
              onChange={(e) => setFields((prev) => ({ ...prev, [f.key]: e.target.value }))}
              disabled={confirmed}
              placeholder={f.kind === "list" ? "comma, separated" : ""}
            />
          </div>
        ))}

        {!confirmed && (
          <div className="flex gap-3 pt-2">
            <Button
              variant="secondary"
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
            >
              {saveMutation.isPending ? "Saving..." : "Save Edits"}
            </Button>
            <Button
              onClick={() => confirmMutation.mutate()}
              disabled={confirmMutation.isPending}
            >
              {confirmMutation.isPending ? "Confirming..." : "Confirm Profile"}
            </Button>
          </div>
        )}
      </div>

      {confirmed && (
        <div className="flex flex-wrap gap-3">
          <Link href={`/dashboard/orgs/${orgId}/compose/learning?profile=${profileId}`}>
            <Button>Compose Learning Path</Button>
          </Link>
          <Link href={`/dashboard/orgs/${orgId}/compose/production?profile=${profileId}`}>
            <Button variant="secondary">Compose Production Solution</Button>
          </Link>
        </div>
      )}

      {profile.raw_request && (
        <details className="rounded-lg border p-4">
          <summary className="cursor-pointer text-sm font-medium">
            Original request
          </summary>
          <p className="mt-2 whitespace-pre-wrap text-sm text-[hsl(var(--muted-foreground))]">
            {profile.raw_request}
          </p>
        </details>
      )}
    </div>
  );
}
