"use client";

import { useParams, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

export default function NewWorkflowPackPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [summary, setSummary] = useState("");
  const [description, setDescription] = useState("");
  const [workflowType, setWorkflowType] = useState("production");
  const [difficulty, setDifficulty] = useState("");
  const [scenarioTags, setScenarioTags] = useState("");
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
        `/orgs/${orgId}/workflow-packs`,
        {
          method: "POST",
          body: JSON.stringify({
            name,
            summary: summary || undefined,
            description: description || undefined,
            workflow_type: workflowType,
            difficulty: difficulty || undefined,
            scenario_tags: scenarioTags
              ? scenarioTags
                  .split(",")
                  .map((t) => t.trim())
                  .filter(Boolean)
              : [],
          }),
        },
      );
      queryClient.invalidateQueries({ queryKey: ["workflow-packs", orgId] });
      router.replace(`/dashboard/orgs/${orgId}/workflow-packs/${res.data.id}`);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to create workflow pack.",
      );
    } finally {
      setLoading(false);
      submitting.current = false;
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">New Workflow Pack</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Package a reusable AI production workflow.
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
            Workflow name
          </label>
          <Input
            id="name"
            required
            minLength={1}
            maxLength={200}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="E-commerce Hero Image Production"
            className="mt-1"
          />
        </div>

        <div>
          <label htmlFor="summary" className="block text-sm font-medium">
            Summary
          </label>
          <Input
            id="summary"
            maxLength={500}
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="A short summary of this workflow"
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
            maxLength={20000}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            placeholder="What this workflow produces, when to use it..."
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="workflowType" className="block text-sm font-medium">
              Workflow type
            </label>
            <select
              id="workflowType"
              value={workflowType}
              onChange={(e) => setWorkflowType(e.target.value)}
              className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            >
              <option value="production">Production</option>
              <option value="pipeline">Pipeline</option>
              <option value="review">Review</option>
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
              <option value="">Not set</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="expert">Expert</option>
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="scenarioTags" className="block text-sm font-medium">
            Scenario tags
          </label>
          <Input
            id="scenarioTags"
            value={scenarioTags}
            onChange={(e) => setScenarioTags(e.target.value)}
            placeholder="ecommerce, product-photography"
            className="mt-1"
          />
          <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
            Comma-separated
          </p>
        </div>

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Creating..." : "Create Workflow Pack"}
        </Button>
      </form>
    </div>
  );
}
