"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { type OrgInfo } from "@/stores/org";

export default function OrgsListPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["my-orgs"],
    queryFn: () => apiWithAuth<{ data: OrgInfo[] }>("/orgs"),
  });

  const orgs = data?.data ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Organizations</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            Manage your training organizations and teams.
          </p>
        </div>
        <Link href="/dashboard/orgs/new">
          <Button>Create Organization</Button>
        </Link>
      </div>

      {isError && <p className="mb-4 text-sm text-red-600">Failed to load organizations. Please try again.</p>}
      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      {!isLoading && orgs.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center">
          <p className="text-[hsl(var(--muted-foreground))]">
            You don&apos;t belong to any organizations yet.
          </p>
          <Link href="/dashboard/orgs/new">
            <Button className="mt-4">Create your first organization</Button>
          </Link>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {orgs.map((org) => (
          <Link
            key={org.id}
            href={`/dashboard/orgs/${org.id}`}
            className="group rounded-lg border p-5 hover:shadow-md transition-shadow"
          >
            <h3 className="font-semibold group-hover:text-[hsl(var(--primary))]">
              {org.name}
            </h3>
            {org.description && (
              <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))] line-clamp-2">
                {org.description}
              </p>
            )}
            <div className="mt-3 flex items-center gap-3 text-xs text-[hsl(var(--muted-foreground))]">
              <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5">
                {org.role}
              </span>
              <span>{org.member_count} members</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
