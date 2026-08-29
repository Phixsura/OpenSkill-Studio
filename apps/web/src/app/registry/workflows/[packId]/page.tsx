"use client";

// Public workflow pack detail: inspect structure, I/O, dependencies and
// version history BEFORE installing (Issue #21 Part A §5).

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

interface PackDetail {
  id: string;
  name: string;
  summary: string | null;
  description: string | null;
  workflow_type: string;
  capability_tags: string[];
  scenario_tags: string[];
  tool_tags: string[];
  install_count: number;
  input_schema: { key: string; type: string; label?: string; required?: boolean }[];
  output_schema: { key: string; type: string }[];
}

interface Release {
  id: string;
  version: string;
  changelog: string | null;
  checksum: string;
  step_count: number;
  released_at: string;
}

interface Preview {
  version: string;
  step_count: number;
  definition: {
    steps?: { id: string; type: string; name: string }[];
    dependencies?: unknown;
  };
  requires_capabilities?: { capability: string; features?: string[] }[];
  recommended_packs?: { family: string; slug: string; version?: string }[];
  inputs?: { key: string; type: string }[];
  outputs?: { key: string; type: string }[];
}

const STEP_TYPE_COLORS: Record<string, string> = {
  instruction: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
  prompt_template: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  asset_input: "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
  transform: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  provider_action: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  review_gate: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  output: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
};

export default function PublicWorkflowPackPage() {
  const { packId } = useParams<{ packId: string }>();

  const { data: packData, isLoading, isError } = useQuery({
    queryKey: ["wf-registry-pack", packId],
    queryFn: () => api<{ data: PackDetail }>(`/registry/workflow-packs/${packId}`),
  });
  const pack = packData?.data;

  const { data: releasesData } = useQuery({
    queryKey: ["wf-registry-releases", packId],
    queryFn: () => api<{ data: Release[] }>(`/registry/workflow-packs/${packId}/releases`),
    enabled: !!pack,
  });
  const releases = releasesData?.data ?? [];

  const { data: previewData } = useQuery({
    queryKey: ["wf-registry-preview", packId],
    queryFn: () => api<{ data: Preview }>(`/registry/workflow-packs/${packId}/preview`),
    enabled: !!pack,
    retry: false,
  });
  const preview = previewData?.data;

  if (isLoading) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-10">
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      </main>
    );
  }

  if (isError || !pack) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-10">
        <p className="text-sm text-red-600">Workflow pack not found.</p>
        <Link href="/registry/workflows" className="mt-2 inline-block text-sm underline">
          ← Back to registry
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-10">
      <Link
        href="/registry/workflows"
        className="text-sm text-[hsl(var(--muted-foreground))] hover:underline"
      >
        ← Workflow Packs
      </Link>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <h1 className="text-3xl font-bold">{pack.name}</h1>
        <span className="rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-medium text-purple-800 dark:bg-purple-900 dark:text-purple-200">
          {pack.workflow_type}
        </span>
      </div>
      {pack.summary && (
        <p className="mt-2 text-lg text-[hsl(var(--muted-foreground))]">{pack.summary}</p>
      )}

      <div className="mt-3 flex flex-wrap gap-1.5">
        {pack.capability_tags.map((cap) => (
          <span
            key={cap}
            className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs"
          >
            {cap.replace(/_/g, " ")}
          </span>
        ))}
      </div>

      <div className="mt-6 rounded-lg border border-dashed p-4 text-sm">
        Install this workflow from your organization dashboard:{" "}
        <Link href="/login?redirect=/dashboard" className="underline">
          Sign in
        </Link>{" "}
        → Workflow Installations → install by pack.
      </div>

      {pack.description && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">About</h2>
          <p className="mt-2 whitespace-pre-wrap text-sm text-[hsl(var(--muted-foreground))]">
            {pack.description}
          </p>
        </section>
      )}

      {/* Typed I/O */}
      <section className="mt-8">
        <h2 className="text-xl font-semibold">Inputs & Outputs</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border p-4">
            <h3 className="text-sm font-semibold">Inputs</h3>
            {pack.input_schema.length === 0 ? (
              <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">None</p>
            ) : (
              <ul className="mt-2 space-y-1.5">
                {pack.input_schema.map((input) => (
                  <li key={input.key} className="flex items-center gap-2 text-sm">
                    <code className="text-xs">{input.key}</code>
                    <span className="rounded bg-[hsl(var(--secondary))] px-1.5 py-0.5 text-xs">
                      {input.type}
                    </span>
                    {input.required !== false && (
                      <span className="text-xs text-[hsl(var(--muted-foreground))]">
                        required
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="rounded-lg border p-4">
            <h3 className="text-sm font-semibold">Outputs</h3>
            {pack.output_schema.length === 0 ? (
              <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">None</p>
            ) : (
              <ul className="mt-2 space-y-1.5">
                {pack.output_schema.map((output) => (
                  <li key={output.key} className="flex items-center gap-2 text-sm">
                    <code className="text-xs">{output.key}</code>
                    <span className="rounded bg-[hsl(var(--secondary))] px-1.5 py-0.5 text-xs">
                      {output.type}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </section>

      {/* Structure preview */}
      {preview?.definition?.steps && preview.definition.steps.length > 0 && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">
            Workflow structure ({preview.step_count} steps · v{preview.version})
          </h2>
          <ol className="mt-3 space-y-2">
            {preview.definition.steps.map((step, i) => (
              <li key={step.id} className="flex items-center gap-3 rounded-md border p-3">
                <span className="text-sm text-[hsl(var(--muted-foreground))]">{i + 1}.</span>
                <span className="text-sm font-medium">{step.name}</span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${STEP_TYPE_COLORS[step.type] ?? ""}`}
                >
                  {step.type.replace(/_/g, " ")}
                </span>
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* Dependencies */}
      {preview &&
        ((preview.requires_capabilities?.length ?? 0) > 0 ||
          (preview.recommended_packs?.length ?? 0) > 0) && (
          <section className="mt-8">
            <h2 className="text-xl font-semibold">Dependencies</h2>
            {preview.requires_capabilities && preview.requires_capabilities.length > 0 && (
              <div className="mt-3">
                <h3 className="text-sm font-semibold">Required provider capabilities</h3>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {preview.requires_capabilities.map((req) => (
                    // key by capability + features: R83 emits one entry per
                    // distinct (capability, feature-set), so the same
                    // capability can appear twice (React duplicate-key warning
                    // + a dropped badge if keyed by capability alone, R84)
                    <span
                      key={`${req.capability}:${(req.features ?? []).join(",")}`}
                      className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-200"
                    >
                      {req.capability.replace(/_/g, " ")}
                      {req.features && req.features.length > 0
                        ? ` (${req.features.join(", ")})`
                        : ""}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {preview.recommended_packs && preview.recommended_packs.length > 0 && (
              <div className="mt-3">
                <h3 className="text-sm font-semibold">Recommended packs</h3>
                <ul className="mt-1 list-inside list-disc text-sm text-[hsl(var(--muted-foreground))]">
                  {preview.recommended_packs.map((rec) => (
                    <li key={rec.slug}>
                      {rec.slug} ({rec.family.replace("_", " ")}
                      {rec.version ? ` ${rec.version}` : ""})
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

      {/* Version history */}
      {releases.length > 0 && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">Version history</h2>
          <div className="mt-3 space-y-2">
            {releases.map((rel) => (
              <div key={rel.id} className="rounded-md border p-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm font-semibold">v{rel.version}</span>
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    {rel.step_count} steps ·{" "}
                    {new Date(rel.released_at).toLocaleDateString()}
                  </span>
                  <code
                    className="ml-auto text-xs text-[hsl(var(--muted-foreground))]"
                    title={rel.checksum}
                  >
                    {rel.checksum.slice(0, 12)}
                  </code>
                </div>
                {rel.changelog && <p className="mt-1.5 text-sm">{rel.changelog}</p>}
              </div>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
