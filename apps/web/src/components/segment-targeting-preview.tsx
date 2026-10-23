"use client";

interface SegmentTargetingPreviewProps { segments: string[]; matchedContent: string[];
  totalRules: number; }

const segIcon: Record<string, string> = {
  new_users: "🆕", power_users: "⚡", paying: "💳", churning: "📉",
  developers: "👨‍💻", enterprise: "🏢",
};

export function SegmentTargetingPreview({ segments, matchedContent, totalRules }: SegmentTargetingPreviewProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Segment Targeting</h2>
      <div>
        <h3 className="text-xs font-medium text-gray-400">User Segments</h3>
        <div className="mt-1 flex flex-wrap gap-1">
          {segments.map(s => (
            <span key={s} className="rounded-full border border-blue-200 bg-blue-50 px-2.5 py-0.5 text-xs dark:border-blue-800 dark:bg-blue-900/10">
              {segIcon[s] ?? "👤"} {s.replace(/_/g, " ")}
            </span>
          ))}
        </div>
      </div>
      <div>
        <h3 className="text-xs font-medium text-gray-400">Matched Content ({matchedContent.length}/{totalRules})</h3>
        <div className="mt-1 space-y-1">
          {matchedContent.map(c => (
            <div key={c} className="flex items-center gap-2 rounded border px-3 py-1.5 text-sm dark:border-gray-700">
              <span className="text-green-500">✓</span>
              <span>{c.replace(/_/g, " ")}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
