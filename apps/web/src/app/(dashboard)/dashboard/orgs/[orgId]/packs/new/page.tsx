"use client";

import { useParams, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

export default function NewPackPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [summary, setSummary] = useState("");
  const [description, setDescription] = useState("");
  const [visibility, setVisibility] = useState("private");
  const [difficulty, setDifficulty] = useState("beginner");
  const [estimatedMinutes, setEstimatedMinutes] = useState("");
  const [scenarioTags, setScenarioTags] = useState("");
  const [toolTags, setToolTags] = useState("");
  const [learningOutcomes, setLearningOutcomes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submitting = useRef(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setError(null);
    setLoading(true);

    try {
      const res = await apiWithAuth<{ data: { id: string } }>(
        `/orgs/${orgId}/packs`,
        {
          method: "POST",
          body: JSON.stringify({
            name,
            summary: summary || undefined,
            description: description || undefined,
            visibility,
            difficulty,
            estimated_minutes: estimatedMinutes
              ? parseInt(estimatedMinutes)
              : undefined,
            scenario_tags: scenarioTags
              ? scenarioTags
                  .split(",")
                  .map((t) => t.trim())
                  .filter(Boolean)
              : [],
            tool_tags: toolTags
              ? toolTags
                  .split(",")
                  .map((t) => t.trim())
                  .filter(Boolean)
              : [],
            learning_outcomes: learningOutcomes
              ? learningOutcomes
                  .split("\n")
                  .map((l) => l.trim())
                  .filter(Boolean)
              : [],
          }),
        },
      );
      queryClient.invalidateQueries({ queryKey: ["packs", orgId] });
      router.push(`/dashboard/orgs/${orgId}/packs/${res.data.id}`);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to create pack.",
      );
    } finally {
      setLoading(false);
      submitting.current = false;
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">New Skill Pack</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Create a new skill pack for your organization.
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium">
            Pack name
          </label>
          <Input
            id="name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="AI Prompt Engineering Essentials"
            className="mt-1"
          />
        </div>

        <div>
          <label htmlFor="summary" className="block text-sm font-medium">
            Summary
          </label>
          <Input
            id="summary"
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="A short summary of this pack"
            className="mt-1"
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            placeholder="Detailed description of skills and outcomes covered..."
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="visibility" className="block text-sm font-medium">
              Visibility
            </label>
            <select
              id="visibility"
              value={visibility}
              onChange={(e) => setVisibility(e.target.value)}
              className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            >
              <option value="private">Private</option>
              <option value="unlisted">Unlisted</option>
              <option value="public">Public</option>
            </select>
          </div>

          <div>
            <label htmlFor="difficulty" className="block text-sm font-medium">
              Difficulty
            </label>
            <select
              id="difficulty"
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="expert">Expert</option>
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="minutes" className="block text-sm font-medium">
            Est. minutes
          </label>
          <Input
            id="minutes"
            type="number"
            min="0"
            value={estimatedMinutes}
            onChange={(e) => setEstimatedMinutes(e.target.value)}
            placeholder="60"
            className="mt-1"
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label
              htmlFor="scenarioTags"
              className="block text-sm font-medium"
            >
              Scenario tags
            </label>
            <Input
              id="scenarioTags"
              value={scenarioTags}
              onChange={(e) => setScenarioTags(e.target.value)}
              placeholder="customer-service, onboarding"
              className="mt-1"
            />
            <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
              Comma-separated
            </p>
          </div>

          <div>
            <label htmlFor="toolTags" className="block text-sm font-medium">
              Tool tags
            </label>
            <Input
              id="toolTags"
              value={toolTags}
              onChange={(e) => setToolTags(e.target.value)}
              placeholder="chatgpt, midjourney, cursor"
              className="mt-1"
            />
            <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
              Comma-separated
            </p>
          </div>
        </div>

        <div>
          <label
            htmlFor="learningOutcomes"
            className="block text-sm font-medium"
          >
            Learning outcomes
          </label>
          <textarea
            id="learningOutcomes"
            value={learningOutcomes}
            onChange={(e) => setLearningOutcomes(e.target.value)}
            rows={4}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            placeholder={"Understand prompt engineering fundamentals\nWrite effective system prompts\nEvaluate AI output quality"}
          />
          <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
            One outcome per line
          </p>
        </div>

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Creating..." : "Create Skill Pack"}
        </Button>
      </form>
    </div>
  );
}
