"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

interface HealthData {
  status: string;
  components?: Record<string, string>;
}

interface OrgItem {
  id: string;
  name: string;
  role: string;
  member_count: number;
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  const { data: health } = useQuery({
    queryKey: ["health-ready"],
    queryFn: () => apiWithAuth<HealthData>("/health/ready"),
    refetchInterval: 60_000,
  });

  const { data: orgsData } = useQuery({
    queryKey: ["my-orgs"],
    queryFn: () => apiWithAuth<{ data: OrgItem[] }>("/orgs"),
  });

  const orgs = orgsData?.data ?? [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">
          Welcome, {user?.display_name ?? "User"}
        </h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Here&apos;s an overview of your OpenSkill Studio workspace.
        </p>
      </div>

      {/* Status cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatusCard
          title="API Status"
          value={health?.status === "ok" ? "Online" : "Checking..."}
          color={health?.status === "ok" ? "green" : "yellow"}
        />
        <StatusCard
          title="Database"
          value={health?.components?.database ?? "—"}
          color={health?.components?.database === "ok" ? "green" : "red"}
        />
        <StatusCard
          title="Cache"
          value={health?.components?.redis ?? "—"}
          color={health?.components?.redis === "ok" ? "green" : "red"}
        />
      </div>

      {/* Organizations */}
      <div>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Your Organizations</h2>
          <Link href="/dashboard/orgs/new">
            <Button size="sm">Create Organization</Button>
          </Link>
        </div>

        {orgs.length === 0 ? (
          <div className="mt-4 rounded-lg border border-dashed p-8 text-center">
            <p className="text-[hsl(var(--muted-foreground))]">
              You haven&apos;t joined any organizations yet.
            </p>
            <Link href="/dashboard/orgs/new">
              <Button className="mt-3">Create your first organization</Button>
            </Link>
          </div>
        ) : (
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {orgs.map((org) => (
              <Link
                key={org.id}
                href={`/dashboard/orgs/${org.id}`}
                className="block rounded-lg border p-4 transition-shadow hover:shadow-md"
              >
                <h3 className="font-semibold">{org.name}</h3>
                <div className="mt-2 flex items-center gap-3 text-xs text-[hsl(var(--muted-foreground))]">
                  <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 capitalize">
                    {org.role}
                  </span>
                  <span>{org.member_count} member{org.member_count !== 1 ? "s" : ""}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Quick links */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Link
          href="/dashboard/portfolio"
          className="rounded-lg border p-5 transition-shadow hover:shadow-sm"
        >
          <h3 className="font-semibold">Portfolio</h3>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            Manage your public profile and showcase your work.
          </p>
        </Link>
        <Link
          href="/dashboard/settings"
          className="rounded-lg border p-5 transition-shadow hover:shadow-sm"
        >
          <h3 className="font-semibold">Settings</h3>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            Update your display name and account preferences.
          </p>
        </Link>
      </div>
    </div>
  );
}

function StatusCard({
  title,
  value,
  color,
}: {
  title: string;
  value: string;
  color: "green" | "red" | "yellow";
}) {
  const colors = {
    green: "text-green-600 dark:text-green-400",
    red: "text-red-600 dark:text-red-400",
    yellow: "text-yellow-600 dark:text-yellow-400",
  };

  return (
    <div className="rounded-lg border p-4">
      <p className="text-sm text-[hsl(var(--muted-foreground))]">{title}</p>
      <p className={`mt-1 text-lg font-semibold ${colors[color]}`}>{value}</p>
    </div>
  );
}
