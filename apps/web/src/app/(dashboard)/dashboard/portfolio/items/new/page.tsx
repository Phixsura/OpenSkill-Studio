"use client";

import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

export default function NewPortfolioItemPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState("");
  const [externalUrl, setExternalUrl] = useState("");
  const [visibility, setVisibility] = useState("public");
  const [featured, setFeatured] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: () =>
      apiWithAuth("/portfolio/items", {
        method: "POST",
        body: JSON.stringify({
          title,
          description: description || undefined,
          tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
          external_url: externalUrl || undefined,
          visibility,
          featured,
        }),
      }),
    onSuccess: () => router.push("/dashboard/portfolio"),
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to create."),
  });

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-3xl font-bold">Add Portfolio Item</h1>

      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          createMutation.mutate();
        }}
        className="space-y-4"
      >
        <div>
          <label htmlFor="title" className="block text-sm font-medium">Title</label>
          <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} required className="mt-1" />
        </div>
        <div>
          <label htmlFor="description" className="block text-sm font-medium">Description (Markdown)</label>
          <textarea
            id="description"
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            rows={5}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Tags (comma separated)</label>
          <Input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="ai, chatbot, python" className="mt-1" />
        </div>
        <div>
          <label className="block text-sm font-medium">External URL</label>
          <Input value={externalUrl} onChange={(e) => setExternalUrl(e.target.value)} placeholder="https://..." className="mt-1" />
        </div>
        <div>
          <label className="block text-sm font-medium">Visibility</label>
          <select
            value={visibility}
            onChange={(e) => setVisibility(e.target.value)}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm"
          >
            <option value="public">Public</option>
            <option value="unlisted">Unlisted (link only)</option>
            <option value="private">Private</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <input type="checkbox" checked={featured} onChange={(e) => setFeatured(e.target.checked)} className="h-4 w-4" />
          <label className="text-sm">Featured on profile</label>
        </div>
        <Button type="submit" disabled={createMutation.isPending}>
          {createMutation.isPending ? "Creating..." : "Create"}
        </Button>
      </form>
    </div>
  );
}
