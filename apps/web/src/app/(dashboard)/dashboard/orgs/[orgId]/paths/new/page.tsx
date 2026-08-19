"use client";

import { useParams, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

export default function NewPathPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [estimatedMinutes, setEstimatedMinutes] = useState("");
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
        `/orgs/${orgId}/paths`,
        {
          method: "POST",
          body: JSON.stringify({
            name,
            description: description || undefined,
            estimated_minutes: estimatedMinutes
              ? Number(estimatedMinutes)
              : undefined,
          }),
        },
      );
      queryClient.invalidateQueries({ queryKey: ["paths", orgId] });
      router.push(`/dashboard/orgs/${orgId}/paths/${res.data.id}`);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to create learning path.",
      );
    } finally {
      setLoading(false);
      submitting.current = false;
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">New Learning Path</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Define a structured learning journey for your organization.
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
            Path name
          </label>
          <Input
            id="name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Frontend Fundamentals"
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
            placeholder="What will learners achieve by completing this path?"
          />
        </div>

        <div>
          <label htmlFor="estimated_minutes" className="block text-sm font-medium">
            Estimated minutes
          </label>
          <Input
            id="estimated_minutes"
            type="number"
            min="0"
            value={estimatedMinutes}
            onChange={(e) => setEstimatedMinutes(e.target.value)}
            placeholder="120"
            className="mt-1"
          />
          <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
            Approximate total time to complete this path.
          </p>
        </div>

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Creating..." : "Create Learning Path"}
        </Button>
      </form>
    </div>
  );
}
