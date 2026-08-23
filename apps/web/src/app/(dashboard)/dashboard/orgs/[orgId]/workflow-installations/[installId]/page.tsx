"use client";

import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, apiWithAuth, ApiError } from "@/lib/api";

interface Installation {
  id: string;
  pack_id: string | null;
  installed_version: string;
  status: string;
  locally_modified: boolean;
  installed_at: string;
  // Effective input schema from the installed release / local definition —
  // works for PRIVATE packs where the public registry 404s.
  input_schema?: InputField[];
}

interface Binding {
  id: string;
  step_id: string;
  binding_mode: string;
  offering_id: string | null;
  reasons: { label?: string; detail?: string }[];
  gaps: { label?: string; detail?: string }[];
  confirmed_by: string | null;
}

interface Offering {
  id: string;
  capability_key: string;
  model_name: string;
  quality_tier: string;
}

interface InputField {
  key: string;
  type: string;
  label: string;
  required: boolean;
  options?: string[] | null;
}

interface Diff {
  steps: { added: string[]; removed: string[]; changed: string[] };
  edges: { added_count: number; removed_count: number };
}

export default function WorkflowInstallationDetailPage() {
  const { orgId, installId } = useParams<{ orgId: string; installId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [upgradeVersion, setUpgradeVersion] = useState("");
  const [diffVersion, setDiffVersion] = useState("");
  const [diff, setDiff] = useState<Diff | null>(null);
  const [runInputs, setRunInputs] = useState<Record<string, string>>({});
  const [bindingEdits, setBindingEdits] = useState<
    Record<string, { offering_id: string; binding_mode: string }>
  >({});

  const { data, isLoading, isError } = useQuery({
    queryKey: ["workflow-installation", orgId, installId],
    queryFn: () =>
      apiWithAuth<{ data: Installation }>(`/orgs/${orgId}/workflow-installations/${installId}`),
  });
  const install = data?.data;

  const { data: bindingsData } = useQuery({
    queryKey: ["workflow-bindings", orgId, installId],
    queryFn: () =>
      apiWithAuth<{ data: Binding[] }>(
        `/orgs/${orgId}/workflow-installations/${installId}/bindings`,
      ),
  });
  const bindings = bindingsData?.data ?? [];

  const { data: offeringsData } = useQuery({
    queryKey: ["provider-offerings", orgId],
    queryFn: () => apiWithAuth<{ data: Offering[] }>(`/orgs/${orgId}/provider-offerings`),
  });
  const offerings = offeringsData?.data ?? [];

  // Pack name (and legacy input_schema fallback) from the public registry —
  // fails silently for PRIVATE packs, which is fine: the authoritative
  // input schema comes from the installation detail itself.
  const { data: packData } = useQuery({
    queryKey: ["registry-workflow-pack", install?.pack_id],
    enabled: !!install?.pack_id,
    queryFn: () =>
      api<{ data: { name: string; input_schema: InputField[] } }>(
        `/registry/workflow-packs/${install!.pack_id}`,
      ).catch(() => null),
  });
  // Prefer the installation's own schema (works for private org packs);
  // fall back to the registry copy only when absent/empty.
  const installSchema = install?.input_schema ?? [];
  const inputSchema =
    installSchema.length > 0 ? installSchema : (packData?.data?.input_schema ?? []);

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["workflow-installation", orgId, installId] });
    queryClient.invalidateQueries({ queryKey: ["workflow-bindings", orgId, installId] });
    queryClient.invalidateQueries({ queryKey: ["workflow-installations", orgId] });
  };

  const upgradeMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/workflow-installations/${installId}/upgrade`, {
        method: "POST",
        body: JSON.stringify({ version: upgradeVersion }),
      }),
    onSuccess: () => {
      setUpgradeVersion("");
      invalidate();
      toast.success("Installation updated");
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Upgrade failed"),
  });

  const forkMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/workflow-installations/${installId}/fork`, {
        method: "POST",
      }),
    onSuccess: () => {
      invalidate();
      toast.success("Installation forked — it no longer tracks the source pack");
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Fork failed"),
  });

  const removeMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/workflow-installations/${installId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflow-installations", orgId] });
      toast.success("Installation removed");
      router.replace(`/dashboard/orgs/${orgId}/workflow-installations`);
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Remove failed"),
  });

  const confirmBindingMutation = useMutation({
    mutationFn: ({ stepId }: { stepId: string }) => {
      // Merge edits over the binding's current values — confirming an
      // auto-suggested binding without touching the selects must send the
      // suggested offering, not undefined (which 422s server-side).
      const edit = bindingEdits[stepId];
      const binding = bindings.find((b) => b.step_id === stepId);
      const offeringId = edit?.offering_id || binding?.offering_id || null;
      const bindingMode = edit?.binding_mode ?? binding?.binding_mode ?? "preferred";
      return apiWithAuth(`/orgs/${orgId}/workflow-installations/${installId}/bindings/${stepId}`, {
        method: "PUT",
        body: JSON.stringify({
          offering_id: offeringId,
          binding_mode: bindingMode,
        }),
      });
    },
    onSuccess: () => {
      invalidate();
      toast.success("Binding confirmed");
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Binding update failed"),
  });

  const startRunMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: { id: string } }>(`/orgs/${orgId}/workflow-runs`, {
        method: "POST",
        body: JSON.stringify({ installation_id: installId, inputs: runInputs }),
      }),
    onSuccess: (res) => {
      toast.success("Run started");
      router.push(`/dashboard/orgs/${orgId}/workflow-runs/${res.data.id}`);
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Run failed to start"),
  });

  const loadDiff = async () => {
    try {
      const res = await apiWithAuth<{ data: Diff }>(
        `/orgs/${orgId}/workflow-installations/${installId}/diff?to=${encodeURIComponent(diffVersion)}`,
      );
      setDiff(res.data);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Diff failed");
    }
  };

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (isError || !install) {
    return <p className="text-sm text-red-600">Failed to load installation.</p>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">
          {packData?.data?.name ?? install.pack_id ?? "Workflow Installation"}
        </h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          v{install.installed_version} · {install.status}
          {install.locally_modified ? " · locally modified" : ""}
        </p>
      </div>

      {/* Run form */}
      <section>
        <h2 className="text-xl font-semibold">Run Workflow</h2>
        <div className="mt-3 space-y-3 rounded-lg border p-4">
          {inputSchema.map((field) => (
            <div key={field.key}>
              <label htmlFor={`run-${field.key}`} className="block text-sm font-medium">
                {field.label || field.key}
                {field.required ? " *" : ""}
                <span className="ml-1 text-xs text-[hsl(var(--muted-foreground))]">
                  ({field.type})
                </span>
              </label>
              {field.type === "selection" && field.options ? (
                <select
                  id={`run-${field.key}`}
                  value={runInputs[field.key] ?? ""}
                  onChange={(e) => setRunInputs({ ...runInputs, [field.key]: e.target.value })}
                  className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm"
                >
                  <option value="">Select…</option>
                  {field.options.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              ) : (
                <Input
                  id={`run-${field.key}`}
                  value={runInputs[field.key] ?? ""}
                  onChange={(e) => setRunInputs({ ...runInputs, [field.key]: e.target.value })}
                  placeholder={
                    ["image", "video", "audio", "reference_asset"].includes(field.type)
                      ? "Asset reference (ULID)"
                      : undefined
                  }
                  className="mt-1"
                />
              )}
            </div>
          ))}
          {inputSchema.length === 0 && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              This workflow declares no inputs.
            </p>
          )}
          <Button
            disabled={startRunMutation.isPending || install.status === "removed"}
            onClick={() => startRunMutation.mutate()}
          >
            {startRunMutation.isPending ? "Starting…" : "Start Run"}
          </Button>
        </div>
      </section>

      {/* Bindings */}
      <section>
        <h2 className="text-xl font-semibold">Provider Bindings</h2>
        <div className="mt-3 space-y-3">
          {bindings.length === 0 && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              No provider-action steps in this workflow.
            </p>
          )}
          {bindings.map((binding) => (
            <div key={binding.id} className="rounded-lg border p-4">
              <div className="flex items-center justify-between">
                <p className="font-mono text-sm font-medium">{binding.step_id}</p>
                {binding.confirmed_by ? (
                  <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-800 dark:bg-green-900 dark:text-green-200">
                    confirmed
                  </span>
                ) : (
                  <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                    suggested
                  </span>
                )}
              </div>
              {binding.gaps.length > 0 && (
                <p className="mt-1 text-xs text-red-600">
                  {binding.gaps.map((g) => g.detail ?? g.label).join("; ")}
                </p>
              )}
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <select
                  value={bindingEdits[binding.step_id]?.offering_id ?? binding.offering_id ?? ""}
                  onChange={(e) =>
                    setBindingEdits({
                      ...bindingEdits,
                      [binding.step_id]: {
                        offering_id: e.target.value,
                        binding_mode:
                          bindingEdits[binding.step_id]?.binding_mode ?? binding.binding_mode,
                      },
                    })
                  }
                  aria-label={`Offering for ${binding.step_id}`}
                  className="rounded-md border bg-transparent px-2 py-1.5 text-sm"
                >
                  <option value="">Select offering…</option>
                  {offerings.map((off) => (
                    <option key={off.id} value={off.id}>
                      {off.model_name} ({off.capability_key}, {off.quality_tier})
                    </option>
                  ))}
                </select>
                <select
                  value={bindingEdits[binding.step_id]?.binding_mode ?? binding.binding_mode}
                  onChange={(e) =>
                    setBindingEdits({
                      ...bindingEdits,
                      [binding.step_id]: {
                        offering_id:
                          bindingEdits[binding.step_id]?.offering_id ?? binding.offering_id ?? "",
                        binding_mode: e.target.value,
                      },
                    })
                  }
                  aria-label={`Binding mode for ${binding.step_id}`}
                  className="rounded-md border bg-transparent px-2 py-1.5 text-sm"
                >
                  <option value="auto">Auto</option>
                  <option value="preferred">Preferred</option>
                  <option value="pinned">Pinned</option>
                </select>
                <Button
                  size="sm"
                  variant="secondary"
                  disabled={
                    confirmBindingMutation.isPending ||
                    !(bindingEdits[binding.step_id]?.offering_id ?? binding.offering_id)
                  }
                  onClick={() => confirmBindingMutation.mutate({ stepId: binding.step_id })}
                >
                  Confirm
                </Button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Upgrade / diff */}
      <section>
        <h2 className="text-xl font-semibold">Upgrade / Rollback</h2>
        <div className="mt-3 space-y-3 rounded-lg border p-4">
          <div className="flex items-end gap-2">
            <div>
              <label htmlFor="diff-version" className="block text-sm font-medium">
                Compare with version
              </label>
              <Input
                id="diff-version"
                value={diffVersion}
                onChange={(e) => setDiffVersion(e.target.value)}
                placeholder="1.1.0"
                className="mt-1 w-32"
              />
            </div>
            <Button size="sm" variant="secondary" disabled={!diffVersion} onClick={loadDiff}>
              Show Diff
            </Button>
          </div>
          {diff && (
            <div className="rounded border p-3 text-sm">
              <p>
                Steps: +{diff.steps.added.length} added, −{diff.steps.removed.length} removed, ~
                {diff.steps.changed.length} changed
              </p>
              {diff.steps.added.length > 0 && (
                <p className="text-xs text-green-700 dark:text-green-300">
                  Added: {diff.steps.added.join(", ")}
                </p>
              )}
              {diff.steps.removed.length > 0 && (
                <p className="text-xs text-red-700 dark:text-red-300">
                  Removed: {diff.steps.removed.join(", ")}
                </p>
              )}
              {diff.steps.changed.length > 0 && (
                <p className="text-xs text-amber-700 dark:text-amber-300">
                  Changed: {diff.steps.changed.join(", ")}
                </p>
              )}
              <p className="mt-1 text-xs">
                Edges: +{diff.edges.added_count} / −{diff.edges.removed_count}
              </p>
            </div>
          )}
          <div className="flex items-end gap-2">
            <div>
              <label htmlFor="upgrade-version" className="block text-sm font-medium">
                Change to version
              </label>
              <Input
                id="upgrade-version"
                value={upgradeVersion}
                onChange={(e) => setUpgradeVersion(e.target.value)}
                placeholder="1.1.0"
                className="mt-1 w-32"
              />
            </div>
            <Button
              size="sm"
              disabled={!upgradeVersion || upgradeMutation.isPending}
              onClick={() => upgradeMutation.mutate()}
            >
              {upgradeMutation.isPending ? "Updating…" : "Apply"}
            </Button>
          </div>
        </div>
      </section>

      {/* Fork / remove */}
      <section>
        <h2 className="text-xl font-semibold">Manage</h2>
        <div className="mt-3 flex gap-2 rounded-lg border p-4">
          {install.status === "active" && (
            <Button
              size="sm"
              variant="secondary"
              disabled={forkMutation.isPending}
              onClick={() => {
                if (window.confirm("Fork this installation? It will stop tracking updates.")) {
                  forkMutation.mutate();
                }
              }}
            >
              Fork (Detach)
            </Button>
          )}
          <Button
            size="sm"
            variant="secondary"
            disabled={removeMutation.isPending}
            onClick={() => {
              if (window.confirm("Remove this workflow installation?")) {
                removeMutation.mutate();
              }
            }}
          >
            Remove
          </Button>
        </div>
      </section>
    </div>
  );
}
