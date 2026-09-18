"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { cn } from "@/lib/utils";

interface Opportunity {
  id: string;
  employer_org_id: string;
  title: string;
  description: string | null;
  opportunity_type: string;
  location_mode: string | null;
  location_text: string | null;
  compensation_display: string | null;
  required_capabilities: CapReq[];
  preferred_capabilities: CapReq[];
  minimum_verification: string | null;
  portfolio_requirements: string | null;
  application_deadline: string | null;
  openings: number;
  status: string;
  created_at: string;
}

interface CapReq {
  capability_id: string;
  min_level: number;
  required?: boolean;
  capability_name?: string;
}

interface CapabilityScore {
  capability_id: string;
  capability_name: string;
  level: number;
  level_label: string;
  score: number;
  evidence_count: number;
}

interface Credential {
  id: string;
  credential_type: string;
  version: number;
  status: string;
  issued_at: string;
}

interface Application {
  id: string;
  opportunity_id: string;
  status: string;
  created_at: string;
}

export default function OpportunityDetailPage() {
  const { opportunityId } = useParams<{ opportunityId: string }>();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();

  const [showApplyForm, setShowApplyForm] = useState(false);
  const [coverNote, setCoverNote] = useState("");
  const [selectedCredentials, setSelectedCredentials] = useState<string[]>([]);

  // Load opportunity
  const { data: oppData, isLoading } = useQuery({
    queryKey: ["opportunity", opportunityId],
    queryFn: () => apiWithAuth<{ data: Opportunity }>(`/talent/opportunities/${opportunityId}`),
  });

  // Load user's capability profile for gap analysis
  const { data: profileData } = useQuery({
    queryKey: ["my-capability-profile", user?.id],
    queryFn: () => apiWithAuth<{ data: CapabilityScore[] }>(`/talent/users/${user?.id}/profile`),
    enabled: !!user?.id,
  });

  // Load user's credentials
  const { data: credsData } = useQuery({
    queryKey: ["my-credentials"],
    queryFn: () => apiWithAuth<{ data: Credential[] }>("/talent/credentials?status=active"),
    enabled: !!user?.id,
  });

  // Check if already applied
  const { data: appsData } = useQuery({
    queryKey: ["my-applications-check", opportunityId],
    queryFn: () =>
      apiWithAuth<{ data: Application[]; meta: { total: number } }>("/talent/applications"),
    enabled: !!user?.id,
  });

  const applyMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/talent/opportunities/${opportunityId}/apply`, {
        method: "POST",
        body: JSON.stringify({
          selected_credentials: selectedCredentials,
          selected_projects: [],
          selected_evidence: [],
          cover_note: coverNote || null,
        }),
      }),
    onSuccess: () => {
      toast.success("Application submitted!");
      queryClient.invalidateQueries({ queryKey: ["my-applications-check"] });
      setShowApplyForm(false);
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Failed to apply"),
  });

  const opp = oppData?.data;
  const profile = profileData?.data ?? [];
  const credentials = credsData?.data ?? [];
  const existingApp = (appsData?.data ?? []).find((a) => a.opportunity_id === opportunityId);

  // Build capability lookup for gap analysis
  const profileMap = new Map(profile.map((s) => [s.capability_id, s]));

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-10 w-2/3 rounded bg-[hsl(var(--secondary))]" />
        <div className="h-40 rounded bg-[hsl(var(--secondary))]" />
      </div>
    );
  }

  if (!opp) {
    return (
      <div className="text-center">
        <p className="text-lg font-medium">Opportunity not found</p>
        <Button variant="outline" className="mt-4" onClick={() => router.back()}>
          Go back
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => router.back()}
          className="mb-3 text-sm text-[hsl(var(--muted-foreground))] hover:underline"
        >
          ← Back to opportunities
        </button>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">{opp.title}</h1>
            <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
              <span className="rounded-full bg-[hsl(var(--secondary))] px-2.5 py-0.5 text-xs font-medium">
                {opp.opportunity_type.replace(/_/g, " ")}
              </span>
              {opp.location_mode && (
                <span>
                  {opp.location_mode === "remote"
                    ? "🌍"
                    : opp.location_mode === "onsite"
                      ? "🏢"
                      : "🔄"}{" "}
                  {opp.location_text ?? opp.location_mode}
                </span>
              )}
              {opp.compensation_display && <span>💰 {opp.compensation_display}</span>}
              <span>
                {opp.openings} opening{opp.openings > 1 ? "s" : ""}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Description */}
      {opp.description && (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-5">
          <h2 className="mb-3 font-semibold">Description</h2>
          <div className="whitespace-pre-wrap text-sm leading-relaxed">{opp.description}</div>
        </div>
      )}

      {/* Required capabilities — with gap analysis */}
      {opp.required_capabilities.length > 0 && (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-5">
          <h2 className="mb-3 font-semibold">Required Capabilities</h2>
          <div className="space-y-2">
            {opp.required_capabilities.map((cap, i) => {
              const userCap = profileMap.get(cap.capability_id);
              const met = userCap && userCap.level >= cap.min_level;
              return (
                <div
                  key={i}
                  className="flex items-center justify-between rounded-md bg-[hsl(var(--secondary))] px-3 py-2"
                >
                  <span className="text-sm">{cap.capability_name ?? cap.capability_id}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      ≥ L{cap.min_level}
                    </span>
                    {userCap ? (
                      <span
                        className={cn(
                          "rounded-full px-2 py-0.5 text-xs font-medium",
                          met
                            ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                            : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
                        )}
                      >
                        {met ? `✓ L${userCap.level}` : `✗ L${userCap.level}`}
                      </span>
                    ) : (
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                        No evidence
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Preferred capabilities */}
      {opp.preferred_capabilities.length > 0 && (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-5">
          <h2 className="mb-3 font-semibold">Preferred Capabilities</h2>
          <div className="flex flex-wrap gap-2">
            {opp.preferred_capabilities.map((cap, i) => {
              const userCap = profileMap.get(cap.capability_id);
              const met = userCap && userCap.level >= cap.min_level;
              return (
                <span
                  key={i}
                  className={cn(
                    "rounded-md px-2.5 py-1 text-xs",
                    met
                      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                      : "bg-[hsl(var(--secondary))]",
                  )}
                >
                  {cap.capability_name ?? cap.capability_id} ≥ L{cap.min_level}
                  {met && " ✓"}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Deadline */}
      {opp.application_deadline && (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-5">
          <p className="text-sm">
            <strong>Application deadline:</strong>{" "}
            {new Date(opp.application_deadline).toLocaleDateString(undefined, {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </p>
        </div>
      )}

      {/* Apply section */}
      <div className="rounded-lg border bg-[hsl(var(--card))] p-5">
        {existingApp ? (
          <div className="text-center">
            <p className="font-medium">You have already applied to this opportunity</p>
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
              Status: <StatusBadge status={existingApp.status} />
            </p>
            <Button
              variant="outline"
              className="mt-3"
              onClick={() => router.push("/dashboard/applications")}
            >
              View my applications
            </Button>
          </div>
        ) : showApplyForm ? (
          <div className="space-y-4">
            <h2 className="font-semibold">Apply</h2>

            {/* Select credentials to share */}
            {credentials.length > 0 && (
              <div>
                <label className="mb-1.5 block text-sm font-medium">
                  Share credentials (optional)
                </label>
                <div className="space-y-1.5">
                  {credentials.map((cred) => (
                    <label
                      key={cred.id}
                      className="flex items-center gap-2 rounded-md bg-[hsl(var(--secondary))] px-3 py-2 text-sm"
                    >
                      <input
                        type="checkbox"
                        checked={selectedCredentials.includes(cred.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCredentials((s) => [...s, cred.id]);
                          } else {
                            setSelectedCredentials((s) => s.filter((id) => id !== cred.id));
                          }
                        }}
                        className="rounded"
                      />
                      {cred.credential_type.replace(/_/g, " ")} v{cred.version}
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Cover note */}
            <div>
              <label className="mb-1.5 block text-sm font-medium">Cover note (optional)</label>
              <textarea
                value={coverNote}
                onChange={(e) => setCoverNote(e.target.value)}
                placeholder="Why are you a great fit for this opportunity?"
                className="w-full rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
                rows={4}
                maxLength={5000}
              />
            </div>

            <div className="flex gap-2">
              <Button onClick={() => applyMutation.mutate()} disabled={applyMutation.isPending}>
                {applyMutation.isPending ? "Submitting…" : "Submit Application"}
              </Button>
              <Button variant="outline" onClick={() => setShowApplyForm(false)}>
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <div className="text-center">
            <Button onClick={() => setShowApplyForm(true)}>Apply Now</Button>
          </div>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    draft: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
    submitted: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
    screening: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
    interview: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
    assessment: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
    offer: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    accepted: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
    withdrawn: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
    hired: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
    completed: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  };
  return (
    <span
      className={cn(
        "inline-block rounded-full px-2.5 py-0.5 text-xs font-medium",
        colors[status] ?? "bg-gray-100 text-gray-800",
      )}
    >
      {status}
    </span>
  );
}
