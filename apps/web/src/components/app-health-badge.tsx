"use client";

import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface AppHealthBadgeProps {
  appId: string;
  /** Show text label next to icon */
  showLabel?: boolean;
}

const STATUS_CONFIG: Record<string, { icon: string; color: string; label: string }> = {
  healthy: { icon: "🟢", color: "text-green-600", label: "Healthy" },
  degraded: { icon: "🟡", color: "text-yellow-600", label: "Degraded" },
  critical: { icon: "🔴", color: "text-red-600", label: "Critical" },
  unknown: { icon: "⚪", color: "text-gray-400", label: "Unknown" },
};

/**
 * AppHealthBadge — compact health status indicator for app listings.
 * Fetches health data and displays a colored icon with optional label.
 */
export function AppHealthBadge({ appId, showLabel = false }: AppHealthBadgeProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["app-health-badge", appId],
    queryFn: () =>
      apiWithAuth<{ data: { status: string } }>(`/developer/apps/${appId}/health`).then(
        (r) => r.data,
      ),
    staleTime: 60_000,
    retry: false,
  });

  if (isLoading) {
    return <span className="inline-block h-3 w-3 animate-pulse rounded-full bg-gray-200" />;
  }

  const status = data?.status ?? "unknown";
  const config = STATUS_CONFIG[status] ?? { icon: "⚪", color: "text-gray-400", label: "Unknown" };

  return (
    <span className={`inline-flex items-center gap-1 ${config.color}`} title={config.label}>
      <span className="text-xs">{config.icon}</span>
      {showLabel && <span className="text-xs font-medium">{config.label}</span>}
    </span>
  );
}
