"use client";

interface AppInstallCountProps {
  count: number;
  trend?: "up" | "down" | "stable";
}

export function AppInstallCount({ count, trend }: AppInstallCountProps) {
  const trendIcon = trend === "up" ? "📈" : trend === "down" ? "📉" : "";
  const formatted = count >= 1000 ? `${(count / 1000).toFixed(1)}k` : String(count);

  return (
    <span className="inline-flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
      📥 {formatted} install{count !== 1 ? "s" : ""} {trendIcon}
    </span>
  );
}
