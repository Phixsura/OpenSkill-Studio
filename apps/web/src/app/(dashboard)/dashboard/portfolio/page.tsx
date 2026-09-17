"use client";

import Link from "next/link";
import { toast } from "sonner";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";

interface ProfileData {
  username: string;
  headline: string | null;
  visibility: string;
}

interface PortfolioItem {
  id: string;
  title: string;
  slug: string;
  visibility: string;
  featured: boolean;
  score: number | null;
  show_score: boolean;
  sort_order?: number;
}

interface SkillBadge {
  id: string;
  skill_name: string;
  category_name: string;
  completion_pct: number;
  completed: boolean;
  show_on_profile: boolean;
}

export default function PortfolioPage() {
  const { data: profileData } = useQuery({
    queryKey: ["portfolio-profile"],
    queryFn: () => apiWithAuth<{ data: ProfileData }>("/portfolio/profile"),
  });

  const { data: itemsData } = useQuery({
    queryKey: ["portfolio-items"],
    queryFn: () => apiWithAuth<{ data: PortfolioItem[] }>("/portfolio/items"),
  });

  const queryClient = useQueryClient();
  const { data: badgesData } = useQuery({
    queryKey: ["portfolio-badges"],
    queryFn: () => apiWithAuth<{ data: SkillBadge[] }>("/portfolio/badges"),
  });

  const toggleBadge = useMutation({
    mutationFn: ({ id, show }: { id: string; show: boolean }) =>
      apiWithAuth(`/portfolio/badges/${id}`, {
        method: "PUT",
        body: JSON.stringify({ show_on_profile: show }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["portfolio-badges"] }),
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Failed to update badge"),
  });

  const deleteItem = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`/talent/portfolio/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      toast.success("Item deleted");
      queryClient.invalidateQueries({ queryKey: ["portfolio-items"] });
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Failed to delete item"),
  });

  const reorderItem = useMutation({
    mutationFn: ({ id, sort_order }: { id: string; sort_order: number }) =>
      apiWithAuth(`/talent/portfolio/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ sort_order }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["portfolio-items"] }),
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Failed to reorder"),
  });

  const profile = profileData?.data;
  const items = itemsData?.data ?? [];
  const badges = badgesData?.data ?? [];

  const moveItem = (index: number, direction: "up" | "down") => {
    const swapIndex = direction === "up" ? index - 1 : index + 1;
    if (swapIndex < 0 || swapIndex >= items.length) return;

    const item = items[index];
    const swapItem = items[swapIndex];
    // Swap sort orders
    reorderItem.mutate({ id: item.id, sort_order: swapItem.sort_order ?? swapIndex });
    reorderItem.mutate({ id: swapItem.id, sort_order: item.sort_order ?? index });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Portfolio</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            Manage your public portfolio and showcase your work.
          </p>
        </div>
        <Link href="/dashboard/portfolio/items/new">
          <Button>Add Project</Button>
        </Link>
      </div>

      {profile && (
        <div className="rounded-lg border p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">Public page</p>
              <a
                href={`/u/${profile.username}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[hsl(var(--primary))] hover:underline"
              >
                openskill.studio/u/{profile.username}
              </a>
            </div>
            <Link href="/dashboard/portfolio/profile">
              <Button variant="secondary">Edit Profile</Button>
            </Link>
          </div>
        </div>
      )}

      {badges.length > 0 && (
        <div className="rounded-lg border p-4">
          <h2 className="text-lg font-semibold">Skill Badges</h2>
          <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
            Earned from completed skills — choose which appear on your public profile.
          </p>
          <div className="mt-3 space-y-2">
            {badges.map((b) => (
              <div
                key={b.id}
                className="flex items-center justify-between rounded-md border px-3 py-2"
              >
                <div>
                  <p className="text-sm font-medium">{b.skill_name}</p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    {b.category_name} · {b.completion_pct}%{b.completed ? " · completed" : ""}
                  </p>
                </div>
                <label className="flex items-center gap-2 text-xs">
                  <input
                    type="checkbox"
                    checked={b.show_on_profile}
                    disabled={toggleBadge.isPending}
                    onChange={(e) => toggleBadge.mutate({ id: b.id, show: e.target.checked })}
                    aria-label={`Show ${b.skill_name} badge on profile`}
                  />
                  Show on profile
                </label>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-2">
        {items.length === 0 && (
          <div className="rounded-lg border border-dashed p-12 text-center text-sm text-[hsl(var(--muted-foreground))]">
            No portfolio items yet. Add your first project.
          </div>
        )}
        {items.map((item, index) => (
          <div key={item.id} className="flex items-center justify-between rounded-lg border p-4">
            <div className="min-w-0 flex-1">
              <h3 className="font-semibold">{item.title}</h3>
              <p className="text-xs capitalize text-[hsl(var(--muted-foreground))]">
                {item.visibility}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {item.featured && (
                <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                  Featured
                </span>
              )}
              {item.show_score && item.score != null && (
                <span className="font-mono text-sm">{item.score}/100</span>
              )}

              {/* Reorder buttons */}
              <div className="flex flex-col">
                <button
                  onClick={() => moveItem(index, "up")}
                  disabled={index === 0 || reorderItem.isPending}
                  className="px-1 text-xs text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] disabled:opacity-30"
                  aria-label="Move up"
                >
                  ▲
                </button>
                <button
                  onClick={() => moveItem(index, "down")}
                  disabled={index === items.length - 1 || reorderItem.isPending}
                  className="px-1 text-xs text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] disabled:opacity-30"
                  aria-label="Move down"
                >
                  ▼
                </button>
              </div>

              {/* Delete button */}
              <button
                onClick={() => {
                  if (confirm(`Delete "${item.title}"? This cannot be undone.`))
                    deleteItem.mutate(item.id);
                }}
                disabled={deleteItem.isPending}
                className="rounded-md border border-red-200 px-2 py-1 text-xs text-red-600 hover:bg-red-50 disabled:opacity-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-950"
                aria-label={`Delete ${item.title}`}
              >
                🗑
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
