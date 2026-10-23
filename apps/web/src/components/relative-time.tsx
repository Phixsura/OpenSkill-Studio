"use client";

interface RelativeTimeProps { relative: string; absolute: string; }

export function RelativeTime({ relative, absolute }: RelativeTimeProps) {
  return (
    <time title={absolute} className="text-xs text-gray-400 cursor-help">
      {relative}
    </time>
  );
}
