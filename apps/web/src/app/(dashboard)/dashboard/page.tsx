"use client";

import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

interface HealthData {
  status: string;
  components?: Record<string, string>;
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  const { data: health } = useQuery({
    queryKey: ["health-ready"],
    queryFn: () => apiWithAuth<HealthData>("/health/ready"),
    refetchInterval: 60_000,
  });

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

      {/* Placeholder sections */}
      <div className="grid gap-4 lg:grid-cols-2">
        <PlaceholderCard
          title="Your Skills"
          description="Track your learning progress across AI skills."
        />
        <PlaceholderCard
          title="Active Projects"
          description="View and submit your project assignments."
        />
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

function PlaceholderCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-lg border border-dashed p-6 text-center">
      <h3 className="font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
        {description}
      </p>
      <p className="mt-3 text-xs text-[hsl(var(--muted-foreground))]">
        Coming soon
      </p>
    </div>
  );
}
