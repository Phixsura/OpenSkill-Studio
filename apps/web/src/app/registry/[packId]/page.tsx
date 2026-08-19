"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

interface PackDetail {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  summary: string | null;
  difficulty: string | null;
  estimated_minutes: number | null;
  install_count: number;
  language: string;
  learning_outcomes: string[];
  scenario_tags: string[];
  tool_tags: string[];
  capability_tags: string[];
  provenance: {
    author_name?: string;
    license_name?: string;
    source_url?: string;
  };
}

interface Release {
  id: string;
  version: string;
  component_count: number;
  changelog: string | null;
  released_at: string;
}

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  intermediate: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  advanced: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  expert: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export default function RegistryPackDetailPage() {
  const { packId } = useParams<{ packId: string }>();

  const { data: packData, isLoading, isError } = useQuery({
    queryKey: ["registry-pack", packId],
    queryFn: () =>
      api<{ data: PackDetail }>(`/registry/packs/${packId}`),
  });

  const { data: releasesData } = useQuery({
    queryKey: ["registry-releases", packId],
    queryFn: () =>
      api<{ data: Release[] }>(`/registry/packs/${packId}/releases`),
  });

  const pack = packData?.data;
  const releases = releasesData?.data ?? [];

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>
      </div>
    );
  }

  if (isError || !pack) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          Pack not found or failed to load.
        </div>
        <Link href="/registry" className="mt-4 inline-block text-sm text-[hsl(var(--primary))] hover:underline">
          ← Back to Registry
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Link href="/registry" className="mb-4 inline-block text-sm text-[hsl(var(--primary))] hover:underline">
        ← Back to Registry
      </Link>

      {/* Pack Header */}
      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold">{pack.name}</h1>
            {pack.provenance?.author_name && (
              <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                by {pack.provenance.author_name}
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            {pack.difficulty && (
              <span className={`rounded-full px-3 py-1 text-sm font-medium ${DIFFICULTY_COLORS[pack.difficulty] ?? ""}`}>
                {pack.difficulty}
              </span>
            )}
            <span className="text-sm text-[hsl(var(--muted-foreground))]">
              {pack.install_count} installs
            </span>
          </div>
        </div>
        {pack.summary && (
          <p className="mt-3 text-lg text-[hsl(var(--muted-foreground))]">
            {pack.summary}
          </p>
        )}
        <Link href="/login">
          <Button className="mt-4">Install in your organization →</Button>
        </Link>
      </div>

      <div className="grid gap-8 md:grid-cols-3">
        {/* Main content */}
        <div className="space-y-6 md:col-span-2">
          {/* Description */}
          {pack.description && (
            <div>
              <h2 className="text-xl font-semibold">Description</h2>
              <p className="mt-2 whitespace-pre-wrap text-sm text-[hsl(var(--muted-foreground))]">
                {pack.description}
              </p>
            </div>
          )}

          {/* Learning Outcomes */}
          {pack.learning_outcomes.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold">What you&apos;ll learn</h2>
              <ul className="mt-2 space-y-1">
                {pack.learning_outcomes.map((outcome, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <span className="mt-0.5 text-green-500">✓</span>
                    {outcome}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Releases */}
          <div>
            <h2 className="text-xl font-semibold">Releases</h2>
            {releases.length === 0 && (
              <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
                No releases yet.
              </p>
            )}
            <div className="mt-2 space-y-3">
              {releases.map((rel) => (
                <div key={rel.id} className="rounded-lg border p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-semibold">v{rel.version}</span>
                      <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
                        {rel.component_count} components
                      </span>
                    </div>
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      {new Date(rel.released_at).toLocaleDateString()}
                    </span>
                  </div>
                  {rel.changelog && (
                    <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
                      {rel.changelog}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {pack.estimated_minutes && (
            <div className="rounded-lg border p-4">
              <h3 className="text-sm font-medium">Estimated time</h3>
              <p className="mt-1 text-lg font-semibold">
                {Math.floor(pack.estimated_minutes / 60)}h {pack.estimated_minutes % 60}m
              </p>
            </div>
          )}

          {pack.provenance?.license_name && (
            <div className="rounded-lg border p-4">
              <h3 className="text-sm font-medium">License</h3>
              <p className="mt-1 text-sm">{pack.provenance.license_name}</p>
            </div>
          )}

          {pack.scenario_tags.length > 0 && (
            <div className="rounded-lg border p-4">
              <h3 className="text-sm font-medium">Scenarios</h3>
              <div className="mt-2 flex flex-wrap gap-1">
                {pack.scenario_tags.map((tag) => (
                  <span key={tag} className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {pack.tool_tags.length > 0 && (
            <div className="rounded-lg border p-4">
              <h3 className="text-sm font-medium">Tools</h3>
              <div className="mt-2 flex flex-wrap gap-1">
                {pack.tool_tags.map((tag) => (
                  <span key={tag} className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {pack.capability_tags.length > 0 && (
            <div className="rounded-lg border p-4">
              <h3 className="text-sm font-medium">Capabilities</h3>
              <div className="mt-2 flex flex-wrap gap-1">
                {pack.capability_tags.map((tag) => (
                  <span key={tag} className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
