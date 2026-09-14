"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface CareerGoal {
  id: string;
  title: string;
  description: string | null;
  target_role: string | null;
  target_capabilities: {
    capability_id: string;
    capability_name?: string;
    target_level: number;
  }[];
  target_date: string | null;
  status: string;
  completed_at: string | null;
}

interface GoalProgress {
  goal_id: string;
  title: string;
  overall_progress: number;
  target_date: string | null;
  days_remaining: number | null;
  capabilities: {
    capability_id: string;
    capability_name: string;
    current_level: number;
    target_level: number;
    progress: number;
    met: boolean;
  }[];
}

interface CapRow {
  capability_name: string;
  capability_id: string;
  target_level: number;
}

const STATUS_BADGE: Record<string, string> = {
  active: "bg-green-100 text-green-700",
  completed: "bg-blue-100 text-blue-700",
  abandoned: "bg-gray-100 text-gray-600",
};

export default function CareerGoalsPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["career-goals"],
    queryFn: () => api<{ data: CareerGoal[] }>("/talent/career-goals"),
  });

  const goals = data?.data ?? [];
  const activeCount = goals.filter((g) => g.status === "active").length;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 animate-pulse rounded bg-[hsl(var(--muted))]" />
        <div className="grid gap-4 sm:grid-cols-2">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-48 animate-pulse rounded-lg border bg-[hsl(var(--muted))]" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">🎯 Career Goals</h1>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            Track your professional development targets
          </p>
        </div>
        {activeCount < 5 && (
          <button
            onClick={() => setShowForm(true)}
            className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] hover:opacity-90"
          >
            + New Goal
          </button>
        )}
      </div>

      {showForm && (
        <CreateGoalForm
          onClose={() => setShowForm(false)}
          onCreated={() => {
            setShowForm(false);
            queryClient.invalidateQueries({ queryKey: ["career-goals"] });
          }}
        />
      )}

      {goals.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center">
          <div className="mb-4 text-4xl">🎯</div>
          <h2 className="text-lg font-semibold">No career goals yet</h2>
          <p className="mt-2 text-[hsl(var(--muted-foreground))]">
            Set a goal to track your skill development journey
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {goals.map((goal) => (
            <GoalCard key={goal.id} goal={goal} />
          ))}
        </div>
      )}
    </div>
  );
}

function GoalCard({ goal }: { goal: CareerGoal }) {
  const queryClient = useQueryClient();

  const { data: progressData } = useQuery({
    queryKey: ["career-goal-progress", goal.id],
    queryFn: () => api<{ data: GoalProgress }>(`/talent/career-goals/${goal.id}/progress`),
    enabled: goal.status === "active",
  });

  const completeMutation = useMutation({
    mutationFn: () => api(`/talent/career-goals/${goal.id}/complete`, { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["career-goals"] }),
  });

  const abandonMutation = useMutation({
    mutationFn: () => api(`/talent/career-goals/${goal.id}/abandon`, { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["career-goals"] }),
  });

  const progress = progressData?.data;
  const daysRemaining = progress?.days_remaining;

  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-5 shadow-sm">
      <div className="mb-3 flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold">{goal.title}</h3>
          {goal.target_role && (
            <p className="mt-0.5 text-sm text-[hsl(var(--muted-foreground))]">
              Target: {goal.target_role}
            </p>
          )}
        </div>
        <span
          className={cn(
            "ml-2 shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold",
            STATUS_BADGE[goal.status] ?? STATUS_BADGE.active,
          )}
        >
          {goal.status}
        </span>
      </div>

      {goal.target_date && (
        <p className="mb-2 text-xs text-[hsl(var(--muted-foreground))]">
          📅 Target: {new Date(goal.target_date).toLocaleDateString()}
          {daysRemaining != null && daysRemaining > 0 && (
            <span className="ml-1">({daysRemaining} days left)</span>
          )}
          {daysRemaining != null && daysRemaining <= 0 && (
            <span className="ml-1 text-red-500">(overdue)</span>
          )}
        </p>
      )}

      {/* Progress bar */}
      {progress && (
        <div className="mb-3">
          <div className="mb-1 flex justify-between text-xs text-[hsl(var(--muted-foreground))]">
            <span>Progress</span>
            <span>{Math.round(progress.overall_progress)}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-[hsl(var(--secondary))]">
            <div
              className="h-full rounded-full bg-[hsl(var(--primary))] transition-all"
              style={{ width: `${Math.min(100, progress.overall_progress)}%` }}
            />
          </div>
        </div>
      )}

      {/* Per-capability progress */}
      {progress && progress.capabilities.length > 0 && (
        <div className="mb-3 space-y-1.5">
          {progress.capabilities.map((cap) => (
            <div key={cap.capability_id} className="flex items-center gap-2 text-xs">
              <span
                className={cn(
                  "inline-block h-2 w-2 shrink-0 rounded-full",
                  cap.met ? "bg-green-500" : cap.progress > 50 ? "bg-yellow-500" : "bg-red-400",
                )}
              />
              <span className="min-w-0 flex-1 truncate">{cap.capability_name}</span>
              <span className="shrink-0 text-[hsl(var(--muted-foreground))]">
                L{cap.current_level} → L{cap.target_level}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      {goal.status === "active" && (
        <div className="flex gap-2 border-t pt-3">
          <button
            onClick={() => completeMutation.mutate()}
            disabled={completeMutation.isPending}
            className="rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50"
          >
            ✓ Complete
          </button>
          <button
            onClick={() => {
              if (confirm("Abandon this goal?")) abandonMutation.mutate();
            }}
            disabled={abandonMutation.isPending}
            className="rounded-md border px-3 py-1.5 text-xs hover:bg-[hsl(var(--secondary))] disabled:opacity-50"
          >
            Abandon
          </button>
        </div>
      )}

      {goal.completed_at && (
        <p className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
          Completed {new Date(goal.completed_at).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}

function CreateGoalForm({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [capabilities, setCapabilities] = useState<CapRow[]>([
    { capability_name: "", capability_id: "", target_level: 3 },
  ]);

  const createMutation = useMutation({
    mutationFn: () =>
      api("/talent/career-goals", {
        method: "POST",
        body: JSON.stringify({
          title,
          description: description || null,
          target_role: targetRole || null,
          target_date: targetDate || null,
          target_capabilities: capabilities
            .filter((c) => c.capability_name.trim())
            .map((c) => ({
              capability_id: c.capability_id || c.capability_name,
              capability_name: c.capability_name,
              target_level: c.target_level,
            })),
        }),
      }),
    onSuccess: onCreated,
  });

  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">Create New Goal</h3>
      <div className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Title *</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Become a Senior AI Designer"
            className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            maxLength={200}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional description..."
            rows={2}
            className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium">Target Role</label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="Senior AI Visual Designer"
              className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Target Date</label>
            <input
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            />
          </div>
        </div>

        {/* Target capabilities */}
        <div>
          <label className="mb-2 block text-sm font-medium">Target Capabilities</label>
          {capabilities.map((cap, i) => (
            <div key={i} className="mb-2 flex items-center gap-2">
              <input
                type="text"
                value={cap.capability_name}
                onChange={(e) => {
                  const next = [...capabilities];
                  next[i] = {
                    capability_name: e.target.value,
                    capability_id: cap.capability_id,
                    target_level: cap.target_level,
                  };
                  setCapabilities(next);
                }}
                placeholder="Capability name"
                className="min-w-0 flex-1 rounded-md border bg-transparent px-3 py-2 text-sm"
              />
              <select
                value={cap.target_level}
                onChange={(e) => {
                  const next = [...capabilities];
                  next[i] = {
                    capability_name: cap.capability_name,
                    capability_id: cap.capability_id,
                    target_level: Number(e.target.value),
                  };
                  setCapabilities(next);
                }}
                className="rounded-md border bg-transparent px-2 py-2 text-sm"
              >
                {[1, 2, 3, 4, 5].map((l) => (
                  <option key={l} value={l}>
                    L{l}
                  </option>
                ))}
              </select>
              {capabilities.length > 1 && (
                <button
                  onClick={() => setCapabilities(capabilities.filter((_, j) => j !== i))}
                  className="shrink-0 text-red-500 hover:text-red-700"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          {capabilities.length < 10 && (
            <button
              onClick={() =>
                setCapabilities([
                  ...capabilities,
                  { capability_name: "", capability_id: "", target_level: 3 },
                ])
              }
              className="text-sm text-[hsl(var(--primary))] hover:underline"
            >
              + Add capability
            </button>
          )}
        </div>

        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="rounded-md border px-4 py-2 text-sm hover:bg-[hsl(var(--secondary))]"
          >
            Cancel
          </button>
          <button
            onClick={() => createMutation.mutate()}
            disabled={!title.trim() || createMutation.isPending}
            className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] hover:opacity-90 disabled:opacity-50"
          >
            {createMutation.isPending ? "Creating…" : "Create Goal"}
          </button>
        </div>
        {createMutation.isError && (
          <p className="text-sm text-red-500">Failed to create goal. Please try again.</p>
        )}
      </div>
    </div>
  );
}
