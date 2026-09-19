"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Application {
  id: string;
  opportunity_id: string;
  user_id: string;
  status: string;
  cover_note: string | null;
  created_at: string;
  updated_at: string;
}

interface Opportunity {
  id: string;
  title: string;
  opportunity_type: string;
  employer_org_id: string;
  location_mode: string | null;
  status: string;
}

interface CursorResponse {
  data: Application[];
  meta: { next_cursor: string | null; has_more: boolean };
}

const STATUS_TABS = [
  { value: "", label: "All" },
  { value: "submitted", label: "Submitted" },
  { value: "screening", label: "Screening" },
  { value: "interview", label: "Interview" },
  { value: "offer", label: "Offer" },
  { value: "hired", label: "Hired" },
  { value: "rejected", label: "Rejected" },
  { value: "withdrawn", label: "Withdrawn" },
];

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  submitted: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  screening: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  interview: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  assessment: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
  offer: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  accepted: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  withdrawn: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  hired: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  completed: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
};

const STATUS_ICONS: Record<string, string> = {
  submitted: "📤",
  screening: "🔍",
  interview: "🎤",
  assessment: "📝",
  offer: "🎉",
  accepted: "✅",
  rejected: "❌",
  withdrawn: "↩️",
  hired: "🏆",
  completed: "🎓",
};

// Pipeline order for the status stepper
const PIPELINE_STAGES = [
  "submitted",
  "screening",
  "interview",
  "assessment",
  "offer",
  "hired",
  "completed",
];

// Statuses from which a candidate can withdraw
const WITHDRAWABLE = new Set(["submitted", "screening", "interview", "assessment"]);

export default function ApplicationsPage() {
  const [statusFilter, setStatusFilter] = useState("");
  const [cursor, setCursor] = useState<string | null>(null);
  const [cursorStack, setCursorStack] = useState<(string | null)[]>([]);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["my-applications", statusFilter, cursor],
    queryFn: () => {
      const params = new URLSearchParams({ limit: "20" });
      if (statusFilter) params.set("status", statusFilter);
      if (cursor) params.set("cursor", cursor);
      return apiWithAuth<CursorResponse>(`/talent/applications?${params}`);
    },
  });

  const applications = data?.data ?? [];
  const meta = data?.meta;

  // Fetch opportunity details for all applications in view
  const oppIds = [...new Set(applications.map((a) => a.opportunity_id))];
  const { data: oppsData } = useQuery({
    queryKey: ["app-opportunities", oppIds.join(",")],
    queryFn: async () => {
      if (oppIds.length === 0) return {};
      const results: Record<string, Opportunity> = {};
      // Fetch each opportunity (could be batched in the future)
      await Promise.all(
        oppIds.map(async (id) => {
          try {
            const resp = await apiWithAuth<{ data: Opportunity }>(`/talent/opportunities/${id}`);
            results[id] = resp.data;
          } catch {
            // Opportunity may have been removed; skip
          }
        }),
      );
      return results;
    },
    enabled: oppIds.length > 0,
  });

  const oppMap = oppsData ?? {};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">My Applications</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Track the status of your opportunity applications.
        </p>
      </div>

      {/* Status tabs */}
      <div className="flex flex-wrap gap-1.5 border-b pb-3">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.value}
            onClick={() => {
              setStatusFilter(tab.value);
              setCursor(null);
              setCursorStack([]);
            }}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm transition-colors",
              statusFilter === tab.value
                ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                : "hover:bg-[hsl(var(--secondary))]",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Applications list */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-lg border bg-[hsl(var(--card))]" />
          ))}
        </div>
      ) : applications.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center">
          <p className="text-lg font-medium">No applications found</p>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            {statusFilter
              ? "No applications with this status."
              : "Browse opportunities to get started."}
          </p>
          <Link href="/dashboard/opportunities">
            <Button className="mt-4">Browse Opportunities</Button>
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {applications.map((app) => (
            <ApplicationCard
              key={app.id}
              application={app}
              opportunity={oppMap[app.opportunity_id]}
              onWithdraw={() => {
                queryClient.invalidateQueries({ queryKey: ["my-applications"] });
              }}
            />
          ))}
        </div>
      )}

      {/* Cursor Pagination */}
      {meta && (cursorStack.length > 0 || cursor !== null || meta.has_more) && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              const prev = cursorStack[cursorStack.length - 1] ?? null;
              setCursor(prev);
              setCursorStack((s) => s.slice(0, -1));
            }}
            disabled={cursorStack.length === 0 && cursor === null}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              if (meta.next_cursor) {
                setCursorStack((s) => [...s, cursor]);
                setCursor(meta.next_cursor);
              }
            }}
            disabled={!meta.has_more}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}

/* ── Status Stepper ──────────────────────────────────────── */

function StatusStepper({ currentStatus }: { currentStatus: string }) {
  // For terminal states (rejected/withdrawn), show them specially
  const isTerminal = currentStatus === "rejected" || currentStatus === "withdrawn";

  const currentIdx = PIPELINE_STAGES.indexOf(currentStatus);
  const activeIdx = isTerminal ? -1 : currentIdx;

  return (
    <div className="flex items-center gap-0.5 overflow-x-auto">
      {PIPELINE_STAGES.slice(0, 5).map((stage, i) => {
        const isPast = !isTerminal && activeIdx >= 0 && i < activeIdx;
        const isCurrent = !isTerminal && i === activeIdx;

        return (
          <div key={stage} className="flex items-center">
            {i > 0 && (
              <div
                className={cn(
                  "h-px w-3 sm:w-5",
                  isPast || isCurrent ? "bg-[hsl(var(--primary))]" : "bg-[hsl(var(--border))]",
                )}
              />
            )}
            <div
              className={cn(
                "flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-bold",
                isCurrent
                  ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                  : isPast
                    ? "bg-[hsl(var(--primary)/0.2)] text-[hsl(var(--primary))]"
                    : "bg-[hsl(var(--secondary))] text-[hsl(var(--muted-foreground))]",
              )}
              title={stage}
            >
              {isPast ? "✓" : i + 1}
            </div>
          </div>
        );
      })}
      {isTerminal && (
        <>
          <div className="h-px w-3 bg-[hsl(var(--border))] sm:w-5" />
          <div
            className={cn(
              "flex h-5 items-center rounded-full px-1.5 text-[9px] font-bold",
              currentStatus === "rejected"
                ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                : "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
            )}
          >
            {currentStatus === "rejected" ? "✕" : "↩"}
          </div>
        </>
      )}
    </div>
  );
}

/* ── Application Card ────────────────────────────────────── */

function ApplicationCard({
  application: app,
  opportunity: opp,
  onWithdraw,
}: {
  application: Application;
  opportunity?: Opportunity;
  onWithdraw: () => void;
}) {
  const [showWithdrawConfirm, setShowWithdrawConfirm] = useState(false);
  const [expanded, setExpanded] = useState(false);

  // Fetch detail data when expanded
  const { data: detailData } = useQuery({
    queryKey: ["application-detail", app.id],
    queryFn: () => apiWithAuth<{ data: { messages: Array<{ id: string; content: string; sender_role: string; created_at: string }>; evidence_bundle: Record<string, unknown>; timeline: Array<{ status: string; changed_at: string }> } }>(`/talent/applications/${app.id}`),
    enabled: expanded,
  });

  const withdrawMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/talent/applications/${app.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: "withdrawn" }),
      }),
    onSuccess: () => {
      toast.success("Application withdrawn");
      onWithdraw();
      setShowWithdrawConfirm(false);
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Failed to withdraw"),
  });

  const statusColor = STATUS_COLORS[app.status] ?? "bg-gray-100 text-gray-800";
  const statusIcon = STATUS_ICONS[app.status] ?? "📋";
  const createdDate = new Date(app.created_at);
  const canWithdraw = WITHDRAWABLE.has(app.status);

  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-5 transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-3">
            <span className="text-lg">{statusIcon}</span>
            <div className="min-w-0">
              <Link
                href={`/dashboard/opportunities/${app.opportunity_id}`}
                className="font-medium hover:underline"
              >
                {opp?.title ?? `Opportunity ${app.opportunity_id.slice(0, 8)}…`}
              </Link>
              <div className="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-[hsl(var(--muted-foreground))]">
                <span>
                  Applied{" "}
                  {createdDate.toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </span>
                {opp?.opportunity_type && (
                  <>
                    <span>·</span>
                    <span className="capitalize">{opp.opportunity_type.replace(/_/g, " ")}</span>
                  </>
                )}
                {opp?.location_mode && (
                  <>
                    <span>·</span>
                    <span className="capitalize">{opp.location_mode}</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        <span
          className={cn(
            "shrink-0 rounded-full px-3 py-1 text-xs font-medium capitalize",
            statusColor,
          )}
        >
          {app.status}
        </span>
      </div>

      {/* Status stepper */}
      <div className="mt-4">
        <StatusStepper currentStatus={app.status} />
      </div>

      {/* Actions */}
      {canWithdraw && (
        <div className="mt-3 border-t pt-3">
          {showWithdrawConfirm ? (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-[hsl(var(--muted-foreground))]">
                Withdraw this application?
              </span>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => withdrawMutation.mutate()}
                disabled={withdrawMutation.isPending}
              >
                {withdrawMutation.isPending ? "Withdrawing…" : "Confirm"}
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setShowWithdrawConfirm(false)}>
                Cancel
              </Button>
            </div>
          ) : (
            <button
              onClick={() => setShowWithdrawConfirm(true)}
              className="text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
            >
              Withdraw application
            </button>
          )}
        </div>
      )}

      {/* Expand toggle */}
      <div className="mt-3 border-t pt-2">
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-[hsl(var(--primary))] hover:underline"
        >
          {expanded ? "▲ Hide details" : "▼ Show details"}
        </button>
      </div>

      {/* Expandable detail panel */}
      {expanded && (
        <div className="mt-3 space-y-4 rounded-md bg-[hsl(var(--secondary)/0.3)] p-4 text-sm">
          {/* Cover note */}
          {app.cover_note && (
            <div>
              <h4 className="mb-1 text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
                Cover Note
              </h4>
              <p className="whitespace-pre-wrap text-[hsl(var(--foreground))]">{app.cover_note}</p>
            </div>
          )}

          {/* Timeline */}
          {detailData?.data?.timeline && detailData.data.timeline.length > 0 && (
            <div>
              <h4 className="mb-2 text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
                Timeline
              </h4>
              <div className="space-y-1.5">
                {detailData.data.timeline.map((event, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <span className="w-2 h-2 rounded-full bg-[hsl(var(--primary))]" />
                    <span className="capitalize font-medium">{event.status.replace(/_/g, " ")}</span>
                    <span className="text-[hsl(var(--muted-foreground))]">
                      {new Date(event.changed_at).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          {detailData?.data?.messages && detailData.data.messages.length > 0 && (
            <div>
              <h4 className="mb-2 text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
                Messages ({detailData.data.messages.length})
              </h4>
              <div className="space-y-2">
                {detailData.data.messages.slice(0, 5).map((msg) => (
                  <div key={msg.id} className="rounded-md border bg-[hsl(var(--card))] p-2.5">
                    <div className="mb-1 flex items-center gap-2 text-xs text-[hsl(var(--muted-foreground))]">
                      <span className="capitalize font-medium">{msg.sender_role}</span>
                      <span>·</span>
                      <span>{new Date(msg.created_at).toLocaleDateString()}</span>
                    </div>
                    <p className="text-xs">{msg.content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Evidence bundle */}
          {detailData?.data?.evidence_bundle && Object.keys(detailData.data.evidence_bundle).length > 0 && (
            <div>
              <h4 className="mb-1 text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
                Evidence Bundle
              </h4>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                {Object.keys(detailData.data.evidence_bundle).length} items attached
              </p>
            </div>
          )}

          {/* Empty state */}
          {!detailData?.data?.timeline?.length && !detailData?.data?.messages?.length && !app.cover_note && (
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              No additional details available yet.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
