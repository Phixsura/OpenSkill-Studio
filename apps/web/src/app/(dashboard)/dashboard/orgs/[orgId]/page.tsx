"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface OrgDetail {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  role: string;
  member_count: number;
  status: string;
  settings: Record<string, unknown>;
  created_at: string;
}

export default function OrgOverviewPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["org", orgId],
    queryFn: () => apiWithAuth<{ data: OrgDetail }>(`/orgs/${orgId}`),
  });

  const org = data?.data;

  if (isLoading) {
    return <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }

  if (isError) {
    return <p className="text-sm text-red-600">Failed to load organization. Please try again.</p>;
  }

  if (!org) {
    return <p className="text-[hsl(var(--muted-foreground))]">Organization not found.</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{org.name}</h1>
        {org.description && (
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">{org.description}</p>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border p-4">
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Members</p>
          <p className="mt-1 text-2xl font-bold">{org.member_count}</p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Your role</p>
          <p className="mt-1 text-2xl font-bold capitalize">{org.role}</p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Status</p>
          <p className="mt-1 text-2xl font-bold capitalize">{org.status}</p>
        </div>
      </div>

      <div className="flex gap-3">
        <Link href={`/dashboard/orgs/${orgId}/members`}>
          <Button variant="secondary">Manage Members</Button>
        </Link>
        {(org.role === "owner" || org.role === "admin") && (
          <Link href={`/dashboard/orgs/${orgId}/settings`}>
            <Button variant="secondary">Settings</Button>
          </Link>
        )}
      </div>
    </div>
  );
}
