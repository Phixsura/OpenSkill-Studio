"use client";

interface RateLimitIndicatorProps { remaining: number; limit: number; resetIn: number; }

export function RateLimitIndicator({ remaining, limit, resetIn }: RateLimitIndicatorProps) {
  const pct = limit > 0 ? (remaining / limit) * 100 : 100;
  const color = pct <= 10 ? "red" : pct <= 30 ? "yellow" : "green";
  return (
    <div className="flex items-center gap-2 text-xs">
      <div className={`h-2 w-2 rounded-full bg-${color}-500`} />
      <span>{remaining}/{limit} remaining</span>
      <span className="text-gray-400">resets in {resetIn}s</span>
    </div>
  );
}
