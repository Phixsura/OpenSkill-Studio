"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface OrgItem {
  id: string;
  name: string;
}

export default function SkillsPage() {
  const { data } = useQuery({
    queryKey: ["my-orgs"],
    queryFn: () => apiWithAuth<{ data: OrgItem[] }>("/orgs"),
  });

  const orgs = data?.data ?? [];

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Skills</h1>
      <p className="text-[hsl(var(--muted-foreground))]">
        Browse skills in your organizations.
      </p>

      {orgs.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-[hsl(var(--muted-foreground))]">
          Join an organization to start learning skills.
        </div>
      ) : (
        <div className="space-y-2">
          {orgs.map((org) => (
            <Link
              key={org.id}
              href={`/dashboard/orgs/${org.id}/skills`}
              className="block rounded-lg border p-4 transition-shadow hover:shadow-sm"
            >
              <p className="font-medium">{org.name}</p>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                View skills →
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
