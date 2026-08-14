"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

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

export default function PortfolioPage() {
  const { data: profileData } = useQuery({
    queryKey: ["portfolio-profile"],
    queryFn: () => apiWithAuth<{ data: ProfileData }>("/portfolio/profile"),
  });

  const { data: itemsData } = useQuery({
    queryKey: ["portfolio-items"],
    queryFn: () => apiWithAuth<{ data: PortfolioItem[] }>("/portfolio/items"),
  });

  const profile = profileData?.data;
  const items = itemsData?.data ?? [];

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
              <a href={`/u/${profile.username}`} target="_blank" rel="noopener noreferrer"
                className="text-[hsl(var(--primary))] hover:underline">
                openskill.studio/u/{profile.username}
              </a>
            </div>
            <Link href="/dashboard/portfolio/profile">
              <Button variant="secondary">Edit Profile</Button>
            </Link>
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
              <p className="text-xs text-[hsl(var(--muted-foreground))] capitalize">{item.visibility}</p>
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
