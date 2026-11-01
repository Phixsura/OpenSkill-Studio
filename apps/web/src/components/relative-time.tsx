"use client";

interface RelativeTimeProps { value: string; label?: string; tooltip?: string; }

export function RelativeTime({ value, label, tooltip }: RelativeTimeProps) {
  return (
    <span className="text-xs text-gray-400" title={tooltip}>
      {label && <span className="mr-1">{label}:</span>}
      {value}
    </span>
  );
}
