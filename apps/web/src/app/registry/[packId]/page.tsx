"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

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
  review_count: number;
  average_rating: number | null;
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

interface PreviewSkill {
  name: string;
  description: string | null;
  difficulty: string | null;
  exercise_count: number;
  prerequisites: string[];
}

interface PreviewTemplate {
  name: string;
  description: string | null;
  rubric_criteria_count: number;
}

interface PreviewCategory {
  name: string;
}

interface PackPreview {
  skills: PreviewSkill[];
  templates: PreviewTemplate[];
  categories: PreviewCategory[];
  total_skills: number;
  total_exercises: number;
  total_templates: number;
}

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  intermediate: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  advanced: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  expert: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

function StarRating({ rating }: { rating: number }) {
  return (
    <span className="inline-flex items-center gap-0.5" aria-label={`${rating.toFixed(1)} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          className={star <= Math.round(rating) ? "text-yellow-500" : "text-gray-300 dark:text-gray-600"}
        >
          ★
        </span>
      ))}
      <span className="ml-1 text-sm font-medium">{rating.toFixed(1)}</span>
    </span>
  );
}

export default function RegistryPackDetailPage() {
  const { packId } = useParams<{ packId: string }>();

  const [isAuthed, setIsAuthed] = useState(false);
  useEffect(() => {
    import("@/stores/auth").then((m) =>
      setIsAuthed(m.useAuthStore.getState().isAuthenticated),
    );
  }, []);

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

  const { data: previewData } = useQuery({
    queryKey: ["registry-preview", packId],
    queryFn: () =>
      api<{ data: PackPreview }>(`/registry/packs/${packId}/preview`),
  });

  const pack = packData?.data;
  const releases = releasesData?.data ?? [];
  const preview = previewData?.data;

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
        <Link href="/registry" aria-label="Back to registry" className="mt-4 inline-block text-sm text-[hsl(var(--primary))] hover:underline">
          &larr; Back to Registry
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Link href="/registry" aria-label="Back to registry" className="mb-4 inline-block text-sm text-[hsl(var(--primary))] hover:underline">
        &larr; Back to Registry
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
            {pack.average_rating != null && (
              <StarRating rating={pack.average_rating} />
            )}
            {pack.review_count > 0 && (
              <span className="text-sm text-[hsl(var(--muted-foreground))]">
                ({pack.review_count} {pack.review_count === 1 ? "review" : "reviews"})
              </span>
            )}
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
        <Link href={isAuthed ? "/dashboard" : "/login"}>
          <Button className="mt-4" aria-label={`Install ${pack.name}`}>
            {isAuthed
              ? "Install in your organization →"
              : "Sign in to install →"}
          </Button>
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
                    <span className="mt-0.5 text-green-500">&#10003;</span>
                    {outcome}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Curriculum (Rich Preview) */}
          {preview && preview.skills.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold">Curriculum</h2>
              <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                {preview.total_skills} {preview.total_skills === 1 ? "skill" : "skills"} &middot;{" "}
                {preview.total_exercises} {preview.total_exercises === 1 ? "exercise" : "exercises"}
              </p>
              <div className="mt-3 space-y-2" role="list">
                {preview.skills.map((skill, i) => (
                  <div key={i} className="rounded-lg border p-3">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{skill.name}</span>
                      <div className="flex items-center gap-2">
                        {skill.difficulty && (
                          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${DIFFICULTY_COLORS[skill.difficulty] ?? ""}`}>
                            {skill.difficulty}
                          </span>
                        )}
                        <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
                          {skill.exercise_count} {skill.exercise_count === 1 ? "exercise" : "exercises"}
                        </span>
                      </div>
                    </div>
                    {skill.description && (
                      <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                        {skill.description}
                      </p>
                    )}
                    {skill.prerequisites.length > 0 && (
                      <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
                        Requires: {skill.prerequisites.join(", ")}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Templates (Rich Preview) */}
          {preview && preview.templates.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold">Templates</h2>
              <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                {preview.total_templates} project {preview.total_templates === 1 ? "template" : "templates"}
              </p>
              <div className="mt-3 space-y-2" role="list">
                {preview.templates.map((tmpl, i) => (
                  <div key={i} className="rounded-lg border p-3">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{tmpl.name}</span>
                      <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
                        {tmpl.rubric_criteria_count} rubric {tmpl.rubric_criteria_count === 1 ? "criterion" : "criteria"}
                      </span>
                    </div>
                    {tmpl.description && (
                      <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                        {tmpl.description}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Version History (Releases) */}
          <div>
            <h2 className="text-xl font-semibold">Version History</h2>
            {releases.length === 0 && (
              <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
                No releases yet.
              </p>
            )}
            {releases.length > 0 && (
              <div className="relative mt-3 ml-3 border-l-2 border-[hsl(var(--border))]">
                {releases.map((rel, i) => (
                  <div key={rel.id} className="relative mb-4 pl-6">
                    <div className="absolute -left-[9px] top-1.5 h-4 w-4 rounded-full border-2 border-[hsl(var(--border))] bg-[hsl(var(--background))]">
                      {i === 0 && (
                        <div className="absolute inset-1 rounded-full bg-[hsl(var(--primary))]" />
                      )}
                    </div>
                    <div className="rounded-lg border p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-semibold">v{rel.version}</span>
                          {i === 0 && (
                            <span className="rounded-full bg-[hsl(var(--primary))] px-2 py-0.5 text-xs text-[hsl(var(--primary-foreground))]">
                              latest
                            </span>
                          )}
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
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Stats summary */}
          {preview && (
            <div className="rounded-lg border p-4">
              <h3 className="text-sm font-medium">Contents</h3>
              <div className="mt-2 space-y-1 text-sm">
                <p>{preview.total_skills} {preview.total_skills === 1 ? "skill" : "skills"}</p>
                <p>{preview.total_exercises} {preview.total_exercises === 1 ? "exercise" : "exercises"}</p>
                <p>{preview.total_templates} {preview.total_templates === 1 ? "template" : "templates"}</p>
                {preview.categories.length > 0 && (
                  <p>{preview.categories.length} {preview.categories.length === 1 ? "category" : "categories"}</p>
                )}
              </div>
            </div>
          )}

          {pack.estimated_minutes != null && pack.estimated_minutes > 0 && (
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
