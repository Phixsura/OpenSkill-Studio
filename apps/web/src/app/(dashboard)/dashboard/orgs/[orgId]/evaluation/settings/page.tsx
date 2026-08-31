"use client";

import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface EvalSettings {
  enabled: boolean;
  monthly_budget_usd: number | null;
  default_model: string;
  auto_evaluate: boolean;
  pass_threshold: number;
}

export default function EvalSettingsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();

  const {
    data: settings,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["eval-settings", orgId],
    queryFn: () =>
      apiWithAuth<{ data: EvalSettings }>(`/orgs/${orgId}/settings/evaluation`).then((r) => r.data),
  });

  const [enabled, setEnabled] = useState(false);
  const [budget, setBudget] = useState("");
  const [model, setModel] = useState("claude-sonnet-5");
  const [autoEval, setAutoEval] = useState(false);
  const [threshold, setThreshold] = useState("0.6");
  const [message, setMessage] = useState<string | null>(null);
  const [synced, setSynced] = useState(false);

  // Sync all fields when data first loads
  useEffect(() => {
    if (settings && !synced) {
      setEnabled(settings.enabled);
      setBudget(settings.monthly_budget_usd?.toString() ?? "");
      setModel(settings.default_model);
      setAutoEval(settings.auto_evaluate);
      setThreshold(settings.pass_threshold?.toString() ?? "0.6");
      setSynced(true);
    }
  }, [settings, synced]);

  const saveMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/settings/evaluation`, {
        method: "PUT",
        body: JSON.stringify({
          enabled,
          // Empty/invalid numeric inputs must not silently become NaN→null
          monthly_budget_usd:
            budget.trim() && !Number.isNaN(parseFloat(budget)) ? parseFloat(budget) : null,
          default_model: model,
          auto_evaluate: autoEval,
          // Only send a threshold when it's a valid number, so a blank field
          // doesn't wipe the stored value
          ...(threshold.trim() && !Number.isNaN(parseFloat(threshold))
            ? { pass_threshold: parseFloat(threshold) }
            : {}),
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["eval-settings", orgId] });
      setMessage("Settings saved.");
    },
    onError: (err) => {
      setMessage(err instanceof ApiError ? err.message : "Failed to save.");
    },
  });

  if (isLoading) return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  if (isError)
    return (
      <p className="text-sm text-red-600">Failed to load evaluation settings. Please try again.</p>
    );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI Evaluation Settings</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Configure AI-powered evaluation for this organization.
        </p>
      </div>

      <div className="max-w-lg space-y-4">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="enabled"
            checked={enabled}
            onChange={(e) => setEnabled(e.target.checked)}
            className="h-4 w-4"
          />
          <label htmlFor="enabled" className="text-sm font-medium">
            Enable AI Evaluation
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium">Default Model</label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm"
          >
            <option value="claude-sonnet-5">Claude Sonnet 5</option>
            <option value="claude-haiku-4-5">Claude Haiku 4.5</option>
            <option value="gpt-4o">GPT-4o</option>
            <option value="gpt-4o-mini">GPT-4o Mini</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium">Monthly Budget (USD)</label>
          <Input
            type="number"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            placeholder="Leave empty for unlimited"
            className="mt-1"
          />
        </div>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="autoEval"
            checked={autoEval}
            onChange={(e) => setAutoEval(e.target.checked)}
            className="h-4 w-4"
          />
          <label htmlFor="autoEval" className="text-sm font-medium">
            Auto-evaluate on submission
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium">Pass Threshold</label>
          <Input
            type="number"
            step="0.1"
            min="0"
            max="1"
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
            className="mt-1 w-32"
          />
          <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
            Score ratio required to auto-approve (0.0–1.0)
          </p>
        </div>

        {message && (
          <p
            className={`text-sm ${message.toLowerCase().includes("fail") ? "text-red-600" : "text-green-600"}`}
          >
            {message}
          </p>
        )}

        <Button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
          {saveMutation.isPending ? "Saving..." : "Save Settings"}
        </Button>
      </div>
    </div>
  );
}
