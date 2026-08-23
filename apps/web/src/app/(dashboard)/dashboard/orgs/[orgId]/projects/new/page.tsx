"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Template {
  id: string;
  name: string;
  description: string;
  project_type: string;
  difficulty: string;
  suggested_minutes: number | null;
  deliverables: { name: string; type: string; required?: boolean }[];
  builtin: boolean;
}

export default function NewProjectPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [instructions, setInstructions] = useState("");
  const [projectType, setProjectType] = useState("general");
  const [maxScore, setMaxScore] = useState("100");
  const [rubricText, setRubricText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [expandedTemplate, setExpandedTemplate] = useState<string | null>(null);

  const submitting = useRef(false);

  const { data: templatesData, isError: templatesError } = useQuery({
    queryKey: ["project-templates", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Template[] }>(`/orgs/${orgId}/project-templates`),
  });
  const templates = templatesData?.data ?? [];

  const handleUseTemplate = async (templateId: string) => {
    if (submitting.current) return;
    submitting.current = true;
    setError(null);
    setLoading(true);
    try {
      const res = await apiWithAuth<{ data: { id: string } }>(
        `/orgs/${orgId}/projects/from-template`,
        {
          method: "POST",
          body: JSON.stringify({ template_id: templateId }),
        },
      );
      queryClient.invalidateQueries({ queryKey: ["projects", orgId] });
      router.replace(`/dashboard/orgs/${orgId}/projects/${res.data.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create from template.");
    } finally {
      setLoading(false);
      submitting.current = false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setError(null);
    setLoading(true);

    try {
      // Parse rubric from text: "Criterion: max_score" per line
      const rubric = rubricText
        .split("\n")
        .filter((l) => l.trim())
        .map((line) => {
          const parts = line.split(":");
          const criterion = parts[0]?.trim() || "General";
          const score = parseInt(parts[1]?.trim() || "25");
          return { criterion, max_score: isNaN(score) ? 25 : score };
        });

      if (rubric.length === 0) {
        rubric.push({ criterion: "Overall Quality", max_score: parseInt(maxScore) || 100 });
      }

      const res = await apiWithAuth<{ data: { id: string } }>(
        `/orgs/${orgId}/projects`,
        {
          method: "POST",
          body: JSON.stringify({
            title,
            description,
            instructions: instructions.trim() || "No instructions provided.",
            project_type: projectType,
            max_score: parseInt(maxScore) || 100,
            rubric,
          }),
        },
      );
      queryClient.invalidateQueries({ queryKey: ["projects", orgId] });
      router.replace(`/dashboard/orgs/${orgId}/projects/${res.data.id}`);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to create project.",
      );
    } finally {
      setLoading(false);
      submitting.current = false;
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">New Project</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Create a project assignment for your organization.
        </p>
      </div>

      {templatesError && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          Failed to load templates.
        </div>
      )}

      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Template gallery */}
      {templates.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold">Start from a template</h2>
          <div className="mt-3 space-y-3">
            {templates.map((t) => (
              <div key={t.id} className="rounded-lg border p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-medium">{t.name}</span>
                      {t.builtin && (
                        <span className="rounded-full bg-[hsl(var(--primary))] px-2 py-0.5 text-xs text-[hsl(var(--primary-foreground))]">
                          Built-in
                        </span>
                      )}
                      {t.project_type === "ai_visual" && (
                        <span className="rounded-full bg-purple-100 px-2 py-0.5 text-xs text-purple-700 dark:bg-purple-900 dark:text-purple-200">
                          AI Visual
                        </span>
                      )}
                      <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs capitalize">
                        {t.difficulty}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                      {t.description}
                    </p>
                    <button
                      type="button"
                      className="mt-1 text-xs text-[hsl(var(--primary))] hover:underline"
                      onClick={() =>
                        setExpandedTemplate(expandedTemplate === t.id ? null : t.id)
                      }
                    >
                      {expandedTemplate === t.id ? "Hide" : "Show"} {t.deliverables.length} workflow
                      stages
                    </button>
                  </div>
                  <Button
                    size="sm"
                    disabled={loading}
                    onClick={() => handleUseTemplate(t.id)}
                  >
                    Use template
                  </Button>
                </div>
                {expandedTemplate === t.id && (
                  <ol className="mt-3 space-y-1 border-t pt-3 text-sm">
                    {t.deliverables.map((d, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <span className="w-5 text-right text-xs text-[hsl(var(--muted-foreground))]">
                          {i + 1}.
                        </span>
                        <span>{d.name}</span>
                        <span className="rounded-full bg-[hsl(var(--secondary))] px-1.5 py-0.5 text-xs capitalize">
                          {d.type.replace("_", " ")}
                        </span>
                        {d.required === false && (
                          <span className="text-xs text-[hsl(var(--muted-foreground))]">
                            optional
                          </span>
                        )}
                      </li>
                    ))}
                  </ol>
                )}
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center gap-3">
            <div className="h-px flex-1 bg-[hsl(var(--border))]" />
            <span className="text-xs uppercase text-[hsl(var(--muted-foreground))]">
              or start blank
            </span>
            <div className="h-px flex-1 bg-[hsl(var(--border))]" />
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium">Project type</label>
          <div className="mt-1 flex gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="project_type"
                value="general"
                checked={projectType === "general"}
                onChange={() => setProjectType("general")}
              />
              General
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="project_type"
                value="ai_visual"
                checked={projectType === "ai_visual"}
                onChange={() => setProjectType("ai_visual")}
              />
              AI Visual (media workflow)
            </label>
          </div>
        </div>
        <div>
          <label htmlFor="title" className="block text-sm font-medium">
            Project title
          </label>
          <Input
            id="title"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="AI Chatbot"
            className="mt-1"
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium">
            Description
          </label>
          <textarea
            id="description"
            required
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            placeholder="What should students build?"
          />
        </div>

        <div>
          <label htmlFor="instructions" className="block text-sm font-medium">
            Instructions (Markdown)
          </label>
          <textarea
            id="instructions"
            required
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            rows={6}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 font-mono text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            placeholder="## Requirements&#10;&#10;1. Build a chatbot..."
          />
        </div>

        <div>
          <label htmlFor="maxScore" className="block text-sm font-medium">
            Max score
          </label>
          <Input
            id="maxScore"
            type="number"
            value={maxScore}
            onChange={(e) => setMaxScore(e.target.value)}
            className="mt-1 w-32"
          />
        </div>

        <div>
          <label htmlFor="rubric" className="block text-sm font-medium">
            Rubric
          </label>
          <textarea
            id="rubric"
            value={rubricText}
            onChange={(e) => setRubricText(e.target.value)}
            rows={4}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 font-mono text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            placeholder={"Functionality: 40\nCode Quality: 30\nInnovation: 30"}
          />
          <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
            One criterion per line: &quot;Name: max_score&quot;
          </p>
        </div>

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Creating..." : "Create Project"}
        </Button>
      </form>
    </div>
  );
}
