"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

export default function NewProjectPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [instructions, setInstructions] = useState("");
  const [maxScore, setMaxScore] = useState("100");
  const [rubricText, setRubricText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
            instructions: instructions || undefined,
            max_score: parseInt(maxScore) || 100,
            rubric,
          }),
        },
      );
      router.push(`/dashboard/orgs/${orgId}/projects/${res.data.id}`);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to create project.",
      );
    } finally {
      setLoading(false);
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

      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
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
