"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface LearningRecommendation {
  capability_id: string;
  capability_name: string;
  current_level: number;
  target_level: number;
  gap_size: number;
  recommended_content: {
    source_type: string;
    source_id: string;
    title: string;
    coverage_weight: number;
  }[];
}

const CONTENT_ICONS: Record<string, string> = {
  skill_pack: "📚",
  assessment_blueprint: "🎯",
  project_template: "📋",
  workflow_pack: "⚙️",
  skill: "📖",
  rubric_criterion: "📏",
  commercial_project: "💼",
};

const GAP_COLORS: Record<number, string> = {
  1: "bg-yellow-100 text-yellow-800",
  2: "bg-orange-100 text-orange-800",
  3: "bg-red-100 text-red-800",
};

export default function LearningPlanPage() {
  const [opportunityId, setOpportunityId] = useState<string>("");

  const queryParams = opportunityId ? `?opportunity_id=${opportunityId}` : "";
  const { data, isLoading, isError } = useQuery({
    queryKey: ["learning-plan", opportunityId],
    queryFn: () => api<{ data: LearningRecommendation[] }>(`/talent/learning-plan${queryParams}`),
  });

  const recommendations = data?.data ?? [];
  const totalGaps = recommendations.length;
  const totalContent = recommendations.reduce((sum, r) => sum + r.recommended_content.length, 0);

  if (isLoading) {
    if (isError) return <div className="p-8 text-center text-red-600">Failed to load data</div>;

  return (
      <div className="space-y-6">
        <div className="h-8 w-56 animate-pulse rounded bg-[hsl(var(--muted))]" />
        <div className="grid gap-4 sm:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-lg border bg-[hsl(var(--muted))]" />
          ))}
        </div>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-40 animate-pulse rounded-lg border bg-[hsl(var(--muted))]" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">📚 My Learning Plan</h1>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            Personalized recommendations to close your skill gaps
          </p>
        </div>
        <div>
          <input
            type="text"
            value={opportunityId}
            onChange={(e) => setOpportunityId(e.target.value)}
            placeholder="Filter by Opportunity ID"
            className="w-full rounded-md border bg-transparent px-3 py-2 text-sm sm:w-64"
          />
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Skill Gaps</p>
          <p className="mt-1 text-2xl font-bold">{totalGaps}</p>
        </div>
        <div className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Recommended Content</p>
          <p className="mt-1 text-2xl font-bold">{totalContent}</p>
        </div>
        <div className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Learning Actions</p>
          <p className="mt-1 text-2xl font-bold">{totalGaps}</p>
        </div>
      </div>

      {/* Recommendations */}
      {recommendations.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center">
          <div className="mb-4 text-4xl">🎉</div>
          <h2 className="text-lg font-semibold">No skill gaps found</h2>
          <p className="mt-2 text-[hsl(var(--muted-foreground))]">
            You&apos;re fully qualified! Keep building evidence to maintain your levels.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec) => (
            <div
              key={rec.capability_id}
              className="rounded-lg border bg-[hsl(var(--card))] p-5 shadow-sm"
            >
              <div className="mb-3 flex items-center gap-3">
                <h3 className="font-semibold">{rec.capability_name}</h3>
                <span className="text-sm text-[hsl(var(--muted-foreground))]">
                  L{rec.current_level} → L{rec.target_level}
                </span>
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-semibold",
                    GAP_COLORS[Math.min(rec.gap_size, 3)] ?? GAP_COLORS[3],
                  )}
                >
                  Gap: {rec.gap_size}
                </span>
              </div>

              {rec.recommended_content.length > 0 ? (
                <div className="space-y-2">
                  {rec.recommended_content.map((content, i) => (
                    <div
                      key={`${content.source_type}-${content.source_id}-${i}`}
                      className="flex items-center gap-3 rounded-md bg-[hsl(var(--secondary))] px-3 py-2"
                    >
                      <span className="text-lg">{CONTENT_ICONS[content.source_type] ?? "📄"}</span>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium">{content.title || content.source_id}</p>
                        <p className="text-xs text-[hsl(var(--muted-foreground))]">
                          {content.source_type.replace(/_/g, " ")}
                        </p>
                      </div>
                      <div className="w-20">
                        <div className="h-1.5 overflow-hidden rounded-full bg-[hsl(var(--muted))]">
                          <div
                            className="h-full rounded-full bg-[hsl(var(--primary))]"
                            style={{ width: `${Math.round(content.coverage_weight * 100)}%` }}
                          />
                        </div>
                        <p className="mt-0.5 text-right text-[10px] text-[hsl(var(--muted-foreground))]">
                          {Math.round(content.coverage_weight * 100)}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  No mapped content available yet — practice independently or request new content.
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
