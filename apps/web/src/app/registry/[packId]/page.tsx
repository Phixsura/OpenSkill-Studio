"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, apiWithAuth } from "@/lib/api";

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

interface PreviewExercise {
  title: string;
}

interface PreviewSkill {
  name: string;
  description: string | null;
  difficulty: string | null;
  exercise_count: number;
  exercises: PreviewExercise[];
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

interface PackReview {
  id: string;
  rating: number;
  title: string;
  body: string | null;
  user_display_name: string | null;
  created_at: string;
}

interface ReviewsResponse {
  data: PackReview[];
  meta: {
    total: number;
    has_more: boolean;
  };
}

interface ReviewStatsData {
  average: number | null;
  total: number;
  distribution: Record<string, number>;
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

function ClickableStarRating({
  value,
  onChange,
}: {
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <span className="inline-flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => onChange(star)}
          className={`text-xl ${star <= value ? "text-yellow-500" : "text-gray-300 dark:text-gray-600"} hover:text-yellow-400 transition-colors`}
          aria-label={`Rate ${star} star${star !== 1 ? "s" : ""}`}
        >
          ★
        </button>
      ))}
    </span>
  );
}

function WriteReviewForm({ packId, onSuccess }: { packId: string; onSuccess: () => void }) {
  const [rating, setRating] = useState(5);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [formError, setFormError] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/registry/packs/${packId}/reviews`, {
        method: "POST",
        body: JSON.stringify({ rating, title, body: body || null }),
      }),
    onSuccess: () => {
      toast.success("Review submitted!");
      setRating(5);
      setTitle("");
      setBody("");
      setFormError("");
      onSuccess();
    },
    onError: (err: Error) => toast.error(err.message || "Failed to submit review"),
  });

  return (
    <div className="rounded-lg border p-4">
      <h3 className="text-lg font-semibold">Write a Review</h3>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          // Validate: low ratings require a body of at least 20 chars
          if (rating <= 2 && (!body || body.trim().length < 20)) {
            setFormError("Reviews with a rating of 2 or below must include a body of at least 20 characters");
            return;
          }
          setFormError("");
          mutation.mutate();
        }}
        className="mt-3 space-y-3"
      >
        <div>
          <label className="mb-1 block text-sm font-medium">Rating</label>
          <ClickableStarRating value={rating} onChange={setRating} />
        </div>
        <div>
          <label htmlFor="review-title" className="mb-1 block text-sm font-medium">Title</label>
          <Input
            id="review-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Summarize your experience"
            required
            maxLength={200}
          />
        </div>
        <div>
          <label htmlFor="review-body" className="mb-1 block text-sm font-medium">Review (optional)</label>
          <textarea
            id="review-body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Share more details about your experience..."
            rows={4}
            maxLength={5000}
            className="block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] placeholder:text-[hsl(var(--muted-foreground))]"
          />
        </div>
        {formError && (
          <p className="text-sm text-red-600 mb-2">{formError}</p>
        )}
        {mutation.isError && (
          <p className="text-sm text-red-600 mb-2">{(mutation.error as Error).message}</p>
        )}
        <Button type="submit" disabled={mutation.isPending || !title.trim()}>
          {mutation.isPending ? "Submitting..." : "Submit Review"}
        </Button>
      </form>
    </div>
  );
}

function ReviewsSection({ packId, isAuthed }: { packId: string; isAuthed: boolean }) {
  const queryClient = useQueryClient();

  const { data: reviewsData } = useQuery({
    queryKey: ["registry-reviews", packId],
    queryFn: () =>
      api<ReviewsResponse>(`/registry/packs/${packId}/reviews`),
  });

  const { data: statsData } = useQuery({
    queryKey: ["registry-review-stats", packId],
    queryFn: () =>
      api<{ data: ReviewStatsData }>(`/registry/packs/${packId}/reviews/stats`),
  });

  const reviews = reviewsData?.data ?? [];
  const stats = statsData?.data;
  const avgRating = stats?.average ?? null;
  const totalReviews = stats?.total ?? 0;
  const distribution = stats?.distribution ?? {};

  const handleReviewSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ["registry-reviews", packId] });
    queryClient.invalidateQueries({ queryKey: ["registry-review-stats", packId] });
    queryClient.invalidateQueries({ queryKey: ["registry-pack", packId] });
  };

  return (
    <div>
      <h2 className="text-xl font-semibold">Reviews</h2>

      {/* Rating summary */}
      {totalReviews > 0 && avgRating != null && (
        <div className="mt-3 flex items-start gap-6 rounded-lg border p-4">
          <div className="text-center">
            <p className="text-4xl font-bold">{avgRating.toFixed(1)}</p>
            <StarRating rating={avgRating} />
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
              {totalReviews} {totalReviews === 1 ? "review" : "reviews"}
            </p>
          </div>
          <div className="flex-1 space-y-1">
            {[5, 4, 3, 2, 1].map((star) => {
              const count = distribution[String(star)] ?? 0;
              const pct = totalReviews > 0 ? (count / totalReviews) * 100 : 0;
              return (
                <div key={star} className="flex items-center gap-2 text-sm">
                  <span className="w-8 text-right">{star} ★</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-[hsl(var(--secondary))]">
                    <div
                      className="h-full rounded-full bg-yellow-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="w-8 text-[hsl(var(--muted-foreground))]">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {totalReviews === 0 && (
        <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
          No reviews yet. Be the first to review this pack!
        </p>
      )}

      {/* Write review form (authenticated only) */}
      {isAuthed && (
        <div className="mt-4">
          <WriteReviewForm packId={packId} onSuccess={handleReviewSuccess} />
        </div>
      )}

      {/* Review list */}
      {reviews.length > 0 && (
        <div className="mt-4 space-y-3">
          {reviews.map((review) => (
            <div key={review.id} className="rounded-lg border p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <StarRating rating={review.rating} />
                  <span className="font-medium">{review.user_display_name || "Anonymous"}</span>
                </div>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {new Date(review.created_at).toLocaleDateString()}
                </span>
              </div>
              <p className="mt-1 font-medium">{review.title}</p>
              {review.body && (
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                  {review.body}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function CurriculumSection({ preview }: { preview: PackPreview }) {
  const [expandedSkills, setExpandedSkills] = useState<Set<number>>(new Set());

  const toggleSkill = (index: number) => {
    setExpandedSkills((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const expandAll = () => {
    setExpandedSkills(new Set(preview.skills.map((_, i) => i)));
  };

  const collapseAll = () => {
    setExpandedSkills(new Set());
  };

  if (preview.skills.length === 0) return null;

  return (
    <div>
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Curriculum</h2>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={expandAll}
            className="text-xs text-[hsl(var(--primary))] hover:underline"
          >
            Expand all
          </button>
          <span className="text-xs text-[hsl(var(--muted-foreground))]">/</span>
          <button
            type="button"
            onClick={collapseAll}
            className="text-xs text-[hsl(var(--primary))] hover:underline"
          >
            Collapse all
          </button>
        </div>
      </div>
      <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
        {preview.total_skills} {preview.total_skills === 1 ? "skill" : "skills"} &middot;{" "}
        {preview.total_exercises} {preview.total_exercises === 1 ? "exercise" : "exercises"}
      </p>
      <div className="mt-3 space-y-2" role="list">
        {preview.skills.map((skill, i) => {
          const isExpanded = expandedSkills.has(i);
          return (
            <div key={i} className="rounded-lg border">
              <button
                type="button"
                onClick={() => toggleSkill(i)}
                className="flex w-full items-center justify-between p-3 text-left hover:bg-[hsl(var(--secondary)/0.5)] transition-colors"
                aria-expanded={isExpanded}
              >
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
                  <span className={`text-sm transition-transform ${isExpanded ? "rotate-180" : ""}`}>
                    &#9662;
                  </span>
                </div>
              </button>
              {isExpanded && (
                <div className="border-t px-3 pb-3 pt-2">
                  {skill.description && (
                    <p className="text-sm text-[hsl(var(--muted-foreground))]">
                      {skill.description}
                    </p>
                  )}
                  {skill.prerequisites.length > 0 && (
                    <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
                      Requires: {skill.prerequisites.join(", ")}
                    </p>
                  )}
                  {skill.exercises.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {skill.exercises.map((ex, j) => (
                        <li key={j} className="flex items-start gap-2 text-sm text-[hsl(var(--muted-foreground))]">
                          <span className="mt-0.5 text-xs">&#9679;</span>
                          {ex.title}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function RegistryPackDetailPage() {
  const { packId } = useParams<{ packId: string }>();

  const [isAuthed, setIsAuthed] = useState(false);
  useEffect(() => {
    // Check auth state. The apiWithAuth client (used by useQuery calls
    // on this page) auto-refreshes the token on 401. We subscribe to
    // the store so we pick up the state as soon as the refresh completes.
    import("@/stores/auth").then((m) => {
      // Check immediately
      if (m.useAuthStore.getState().isAuthenticated) {
        setIsAuthed(true);
        return;
      }
      // Subscribe to store changes — the apiWithAuth auto-refresh
      // will update the store when the refresh token cookie is valid.
      const unsub = m.useAuthStore.subscribe((state) => {
        if (state.isAuthenticated) {
          setIsAuthed(true);
          unsub();
        }
      });
      // Cleanup on unmount
      return () => unsub();
    });
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
              {pack.install_count} install{pack.install_count !== 1 ? "s" : ""}
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

          {/* Curriculum (Rich Preview with expand/collapse) */}
          {preview && <CurriculumSection preview={preview} />}

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

          {/* Reviews */}
          <ReviewsSection packId={packId} isAuthed={isAuthed} />
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
                {pack.estimated_minutes >= 60 ? `${Math.floor(pack.estimated_minutes / 60)}h ` : ""}{pack.estimated_minutes % 60}m
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
