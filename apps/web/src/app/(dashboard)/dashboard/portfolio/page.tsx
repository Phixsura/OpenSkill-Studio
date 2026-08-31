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

  const profile = profileData?.data;
  const items = itemsData?.data ?? [];
  const badges = badgesData?.data ?? [];

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
        {items.map((item) => (
          <div key={item.id} className="flex items-center justify-between rounded-lg border p-4">
            <div>
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
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
