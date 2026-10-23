"use client";

interface RelativeTimeProps { date: string; className?: string; }

function getRelativeTime(isoDate: string): string {
  try {
    const dt = new Date(isoDate);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - dt.getTime()) / 1000);
    if (seconds < 60) return "just now";
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    if (days < 30) return `${Math.floor(days / 7)}w ago`;
    if (days < 365) return `${Math.floor(days / 30)}mo ago`;
    return `${Math.floor(days / 365)}y ago`;
  } catch {
    return isoDate;
  }
}

export function RelativeTime({ date, className = "" }: RelativeTimeProps) {
  const relative = getRelativeTime(date);
  return (
    <time dateTime={date} title={new Date(date).toLocaleString()} className={`text-gray-400 ${className}`}>
      {relative}
    </time>
  );
}
