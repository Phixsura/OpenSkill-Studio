"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface PathwayProgress {
  completed: boolean;
  pathway_id: string;
  pathway_name: string;
  target_credential_type: string;
  required_count: number;
  earned_count: number;
  earned_credentials: { credential_type: string; issued_at: string }[];
  missing_credential_types: string[];
}

export default function CredentialPathwaysPage() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["credential-pathways-progress"],
    queryFn: () => api<{ data: PathwayProgress[] }>("/talent/credential-pathways/my-progress"),
  });

  const pathways = data?.data ?? [];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-56 animate-pulse rounded bg-[hsl(var(--muted))]" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-56 animate-pulse rounded-lg border bg-[hsl(var(--muted))]" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">🏆 Credential Pathways</h1>
        <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
          Earn advanced credentials by completing prerequisite badges
        </p>
      </div>

      {pathways.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center">
          <div className="mb-4 text-4xl">🏆</div>
          <h2 className="text-lg font-semibold">No credential pathways available yet</h2>
          <p className="mt-2 text-[hsl(var(--muted-foreground))]">
            Pathways will appear here when your organization sets them up.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {pathways.map((pw) => (
            <PathwayCard key={pw.pathway_id} pathway={pw} queryClient={queryClient} />
          ))}
        </div>
      )}
    </div>
  );
}

function PathwayCard({
  pathway: pw,
  queryClient,
}: {
  pathway: PathwayProgress;
  queryClient: ReturnType<typeof useQueryClient>;
}) {
  const progressPct =
    pw.required_count > 0 ? Math.round((pw.earned_count / pw.required_count) * 100) : 0;

  const issueMutation = useMutation({
    mutationFn: () =>
      api(`/talent/credential-pathways/${pw.pathway_id}/check-issue`, { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["credential-pathways-progress"] }),
  });

  return (
    <div className="flex flex-col rounded-lg border bg-[hsl(var(--card))] p-5 shadow-sm">
      {/* Header */}
      <div className="mb-3">
        <h3 className="font-semibold">{pw.pathway_name}</h3>
        <span className="mt-1 inline-block rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-semibold text-purple-700">
          {pw.target_credential_type}
        </span>
      </div>

      {/* Progress bar */}
      <div className="mb-3">
        <div className="mb-1 flex justify-between text-xs text-[hsl(var(--muted-foreground))]">
          <span>
            {pw.earned_count} of {pw.required_count} required
          </span>
          <span>{progressPct}%</span>
        </div>
        <div className="h-2.5 overflow-hidden rounded-full bg-[hsl(var(--secondary))]">
          <div
            className={cn(
              "h-full rounded-full transition-all",
              pw.completed ? "bg-green-500" : "bg-[hsl(var(--primary))]",
            )}
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Prerequisites checklist */}
      <div className="mb-4 flex-1 space-y-1.5">
        {pw.earned_credentials.map((cred) => (
          <div key={cred.credential_type} className="flex items-center gap-2 text-sm">
            <span className="text-green-500">✅</span>
            <span>{cred.credential_type}</span>
          </div>
        ))}
        {pw.missing_credential_types.map((ct) => (
          <div
            key={ct}
            className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]"
          >
            <span>⬜</span>
            <span>{ct}</span>
          </div>
        ))}
      </div>

      {/* Actions */}
      {pw.completed && (
        <div className="border-t pt-3">
          <div className="mb-2 text-center text-sm font-medium text-green-600">
            🎉 Eligible for auto-issuance!
          </div>
          <button
            onClick={() => issueMutation.mutate()}
            disabled={issueMutation.isPending}
            className="w-full rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
          >
            {issueMutation.isPending ? "Issuing…" : "Check & Issue Credential"}
          </button>
          {issueMutation.isSuccess && (
            <p className="mt-2 text-center text-xs text-green-600">
              Credential issued successfully!
            </p>
          )}
        </div>
      )}
    </div>
  );
}
