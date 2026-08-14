"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface HealthData {
  status: string;
}

export default function HealthPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: () => api<HealthData>("/health"),
    refetchInterval: 30_000,
  });

  const status = isLoading
    ? "Checking..."
    : isError
      ? "Offline"
      : data?.status === "ok"
        ? "Online"
        : "Error";

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-semibold">System Health</h1>
      <p className="text-lg">
        API Status:{" "}
        <span
          className={`font-mono font-bold ${status === "Online" ? "text-green-600" : "text-red-600"}`}
        >
          {status}
        </span>
      </p>
    </main>
  );
}
