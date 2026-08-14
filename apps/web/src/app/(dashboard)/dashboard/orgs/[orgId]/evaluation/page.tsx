"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface EvalTask {
  id: string;
  type: string;
  status: string;
  llm_model: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  cost_usd: number | null;
  created_at: string;
}

interface Usage {
  total_tasks: number;
  total_cost_usd: number;
  budget_usd: number | null;
  budget_remaining: number | null;
  month: string;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "text-yellow-600",
  processing: "text-blue-600",
  completed: "text-green-600",
  failed: "text-red-600",
  cancelled: "text-gray-500",
};

export default function EvaluationPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data: tasksData } = useQuery({
    queryKey: ["eval-tasks", orgId],
    queryFn: () =>
      apiWithAuth<{ data: EvalTask[]; meta: { total: number } }>(
        `/orgs/${orgId}/evaluation/tasks`,
      ),
  });

  const { data: usage } = useQuery({
    queryKey: ["eval-usage", orgId],
    queryFn: () => apiWithAuth<Usage>(`/orgs/${orgId}/evaluation/usage`),
  });

  const tasks = tasksData?.data ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Evaluation</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            Manage AI-powered grading and evaluation tasks.
          </p>
        </div>
        <Link href={`/dashboard/orgs/${orgId}/evaluation/settings`}>
          <Button variant="secondary">Settings</Button>
        </Link>
      </div>

      {/* Usage stats */}
      {usage && (
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-lg border p-4">
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Tasks This Month</p>
            <p className="mt-1 text-2xl font-bold">{usage.total_tasks}</p>
          </div>
          <div className="rounded-lg border p-4">
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Cost This Month</p>
            <p className="mt-1 text-2xl font-bold">${usage.total_cost_usd.toFixed(2)}</p>
          </div>
          <div className="rounded-lg border p-4">
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Budget Remaining</p>
            <p className="mt-1 text-2xl font-bold">
              {usage.budget_remaining !== null
                ? `$${usage.budget_remaining.toFixed(2)}`
                : "Unlimited"}
            </p>
          </div>
        </div>
      )}

      {/* Tasks table */}
      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-[hsl(var(--secondary))]">
            <tr>
              <th className="px-4 py-3 text-left">ID</th>
              <th className="px-4 py-3 text-left">Type</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-left">Model</th>
              <th className="px-4 py-3 text-right">Cost</th>
              <th className="px-4 py-3 text-left">Created</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((t) => (
              <tr key={t.id} className="border-t">
                <td className="px-4 py-3 font-mono text-xs">{t.id.slice(0, 12)}...</td>
                <td className="px-4 py-3 capitalize">{t.type.replace("_", " ")}</td>
                <td className={`px-4 py-3 capitalize font-medium ${STATUS_COLORS[t.status] ?? ""}`}>
                  {t.status}
                </td>
                <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                  {t.llm_model ?? "—"}
                </td>
                <td className="px-4 py-3 text-right font-mono">
                  {t.cost_usd !== null ? `$${Number(t.cost_usd).toFixed(4)}` : "—"}
                </td>
                <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                  {new Date(t.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
            {tasks.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-[hsl(var(--muted-foreground))]">
                  No evaluation tasks yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {tasksData?.meta && tasks.length < tasksData.meta.total && (
        <p className="text-center text-sm text-[hsl(var(--muted-foreground))]">
          Showing {tasks.length} of {tasksData.meta.total} tasks
        </p>
      )}
    </div>
  );
}
