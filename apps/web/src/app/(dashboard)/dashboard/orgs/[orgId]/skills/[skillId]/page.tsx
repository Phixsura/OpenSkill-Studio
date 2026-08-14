"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { apiWithAuth } from "@/lib/api";

interface SkillDetail {
  id: string;
  name: string;
  description: string;
  learning_content: string | null;
  difficulty: string;
  estimated_minutes: number | null;
  tags: string[];
  prerequisites: { id: string; name: string; slug: string }[];
}

interface ExerciseItem {
  id: string;
  title: string;
  description: string;
  type: string;
  max_score: number;
}

export default function SkillDetailPage() {
  const { orgId, skillId } = useParams<{ orgId: string; skillId: string }>();

  const { data: skillData, isLoading, isError } = useQuery({
    queryKey: ["skill", orgId, skillId],
    queryFn: () => apiWithAuth<{ data: SkillDetail }>(`/orgs/${orgId}/skills/${skillId}`),
  });

  const { data: exerciseData } = useQuery({
    queryKey: ["exercises", orgId, skillId],
    queryFn: () =>
      apiWithAuth<{ data: ExerciseItem[] }>(`/orgs/${orgId}/skills/${skillId}/exercises`),
  });

  const skill = skillData?.data;
  const exercises = exerciseData?.data ?? [];

  if (isLoading) {
    return <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (isError || !skill) {
    return <p className="text-[hsl(var(--destructive))]">Failed to load skill.</p>;
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_300px]">
      {/* Main content */}
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold">{skill.name}</h1>
          <p className="mt-2 text-[hsl(var(--muted-foreground))]">{skill.description}</p>
        </div>

        {/* Learning content */}
        {skill.learning_content && (
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {skill.learning_content}
            </ReactMarkdown>
          </div>
        )}

        {/* Exercises */}
        <div>
          <h2 className="text-xl font-semibold">Exercises</h2>
          <div className="mt-4 space-y-3">
            {exercises.length === 0 && (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                No exercises yet.
              </p>
            )}
            {exercises.map((ex, i) => (
              <Link
                key={ex.id}
                href={`/dashboard/orgs/${orgId}/skills/${skillId}/exercises/${ex.id}`}
                className="flex items-center gap-4 rounded-lg border p-4 transition-shadow hover:shadow-sm"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[hsl(var(--secondary))] text-sm font-medium">
                  {i + 1}
                </span>
                <div className="flex-1">
                  <p className="font-medium">{ex.title}</p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))] capitalize">
                    {ex.type.replace("_", " ")} · {ex.max_score} pts
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <aside className="space-y-4">
        <div className="rounded-lg border p-4">
          <h3 className="text-sm font-semibold">Details</h3>
          <dl className="mt-3 space-y-2 text-sm">
            <div>
              <dt className="text-[hsl(var(--muted-foreground))]">Difficulty</dt>
              <dd className="capitalize">{skill.difficulty}</dd>
            </div>
            {skill.estimated_minutes && (
              <div>
                <dt className="text-[hsl(var(--muted-foreground))]">Est. time</dt>
                <dd>{skill.estimated_minutes} min</dd>
              </div>
            )}
            <div>
              <dt className="text-[hsl(var(--muted-foreground))]">Exercises</dt>
              <dd>{exercises.length}</dd>
            </div>
          </dl>
        </div>

        {(skill.prerequisites ?? []).length > 0 && (
          <div className="rounded-lg border p-4">
            <h3 className="text-sm font-semibold">Prerequisites</h3>
            <ul className="mt-2 space-y-1">
              {(skill.prerequisites ?? []).map((p) => (
                <li key={p.id}>
                  <Link
                    href={`/dashboard/orgs/${orgId}/skills/${p.id}`}
                    className="text-sm hover:underline"
                  >
                    {p.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}

        {(skill.tags ?? []).length > 0 && (
          <div className="rounded-lg border p-4">
            <h3 className="text-sm font-semibold">Tags</h3>
            <div className="mt-2 flex flex-wrap gap-1">
              {(skill.tags ?? []).map((tag) => (
                <span
                  key={tag}
                  className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}
