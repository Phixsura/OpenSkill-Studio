"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Category {
  id: string;
  name: string;
}

export default function NewSkillPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: catData } = useQuery({
    queryKey: ["categories", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Category[] }>(`/orgs/${orgId}/categories`),
  });

  const categories = catData?.data ?? [];

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [difficulty, setDifficulty] = useState("beginner");
  const [tags, setTags] = useState("");
  const [estimatedMinutes, setEstimatedMinutes] = useState("");
  const [learningContent, setLearningContent] = useState("");
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
        `/orgs/${orgId}/skills`,
        {
          method: "POST",
          body: JSON.stringify({
            name,
            description,
            category_id: categoryId || undefined,
            difficulty,
            tags: tags
              ? tags
                  .split(",")
                  .map((t) => t.trim())
                  .filter(Boolean)
              : [],
            estimated_minutes: estimatedMinutes
              ? parseInt(estimatedMinutes)
              : undefined,
            learning_content: learningContent || undefined,
          }),
        },
      );
      queryClient.invalidateQueries({ queryKey: ["skills", orgId] });
      router.push(`/dashboard/orgs/${orgId}/skills/${res.data.id}`);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to create skill.",
      );
    } finally {
      setLoading(false);
      submitting.current = false;
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">New Skill</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Create a new learning skill for your organization.
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
            Skill name
          </label>
          <Input
            id="name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Prompt Engineering"
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
            placeholder="What will learners achieve?"
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="category" className="block text-sm font-medium">
              Category
            </label>
            {categories.length === 0 ? (
              <p className="mt-1 text-sm text-[hsl(var(--destructive))]">
                No categories yet. Create a category first via the API or ask an admin.
              </p>
            ) : (
              <select
                id="category"
                required
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value)}
                className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
              >
                <option value="">Select category</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            )}
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
            </select>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="tags" className="block text-sm font-medium">
              Tags
            </label>
            <Input
              id="tags"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="ai, prompting, llm"
              className="mt-1"
            />
            <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
              Comma-separated
            </p>
          </div>

          <div>
            <label htmlFor="minutes" className="block text-sm font-medium">
              Est. minutes
            </label>
            <Input
              id="minutes"
              type="number"
              value={estimatedMinutes}
              onChange={(e) => setEstimatedMinutes(e.target.value)}
              placeholder="30"
              className="mt-1"
            />
          </div>
        </div>

        <div>
          <label
            htmlFor="learningContent"
            className="block text-sm font-medium"
          >
            Learning Content (Markdown)
          </label>
          <textarea
            id="learningContent"
            value={learningContent}
            onChange={(e) => setLearningContent(e.target.value)}
            rows={8}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 font-mono text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            placeholder="# Introduction&#10;&#10;Write your learning content here..."
          />
        </div>

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Creating..." : "Create Skill"}
        </Button>
      </form>
    </div>
  );
}
