"use client";

interface PostmortemViewerProps { title: string; severity: string; durationMinutes: number;
  usersAffected: number; rootCause: string; actionItems: string[]; status: string; }

const SEV_STYLE: Record<string, string> = { critical: "bg-red-500", high: "bg-orange-500", medium: "bg-yellow-500", low: "bg-blue-500" };

export function PostmortemViewer({ title, severity, durationMinutes, usersAffected, rootCause, actionItems, status }: PostmortemViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white ${SEV_STYLE[severity] ?? "bg-gray-500"}`}>
        <h3 className="font-bold">{title}</h3>
        <p className="text-xs opacity-80">{severity} · {durationMinutes}min · {usersAffected.toLocaleString()} users</p>
      </div>
      <div className="p-4 space-y-3 text-xs">
        <div><span className="font-semibold">Root Cause:</span> <span className="text-gray-600 dark:text-gray-400">{rootCause}</span></div>
        <div>
          <span className="font-semibold">Action Items ({status}):</span>
          <ul className="mt-1 space-y-0.5 pl-3">
            {actionItems.map((a, i) => <li key={i} className="text-gray-600 dark:text-gray-400">• {a}</li>)}
          </ul>
        </div>
      </div>
    </div>
  );
}
