"use client";

interface DigestProps { period: string; totalEvents: number; highlights: string[]; byType: Record<string, number>; }

export function NotificationDigest({ period, totalEvents, highlights, byType }: DigestProps) {
  if (totalEvents === 0) return <p className="py-3 text-center text-sm text-gray-400">No activity this {period}</p>;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-2 flex items-center justify-between">
        <h4 className="font-semibold capitalize">{period} Digest</h4>
        <span className="text-xs text-gray-500">{totalEvents} events</span>
      </div>
      {highlights.length > 0 && (
        <ul className="mb-3 space-y-1">{highlights.map((h, i) => <li key={i} className="text-sm">{h}</li>)}</ul>
      )}
      <div className="flex flex-wrap gap-2">
        {Object.entries(byType).map(([type, count]) => (
          <span key={type} className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-800">{type}: {count}</span>
        ))}
      </div>
    </div>
  );
}
