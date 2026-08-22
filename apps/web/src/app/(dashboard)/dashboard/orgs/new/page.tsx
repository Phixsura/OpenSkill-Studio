"use client";

import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

export default function CreateOrgPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const autoSlug = name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 100);

  const submitting = useRef(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setError(null);
    setLoading(true);

    try {
      const res = await apiWithAuth<{ data: { id: string } }>("/orgs", {
        method: "POST",
        body: JSON.stringify({
          name,
          slug: slug || autoSlug || undefined,
          description: description || undefined,
        }),
      });
      queryClient.invalidateQueries({ queryKey: ["my-orgs"] });
      router.push(`/dashboard/orgs/${res.data.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create organization.");
    } finally {
      setLoading(false);
      submitting.current = false;
    }
  };

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Create Organization</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Set up a new training organization or team.
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
            Organization name
          </label>
          <Input
            id="name"
            required
            minLength={2}
            maxLength={100}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="AI Creators Academy"
            className="mt-1"
          />
        </div>

        <div>
          <label htmlFor="slug" className="block text-sm font-medium">
            URL slug
          </label>
          <Input
            id="slug"
            maxLength={100}
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            placeholder={autoSlug || "auto-generated"}
            className="mt-1"
          />
          <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
            Leave empty to auto-generate from name.
          </p>
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
            maxLength={2000}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            placeholder="What is this organization about?"
          />
        </div>

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Creating..." : "Create Organization"}
        </Button>
      </form>
    </div>
  );
}
