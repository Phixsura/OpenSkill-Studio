"use client";

interface Release { releaseId: string; version: string; status: string; changelog: string[]; reviewComment: string; }

const statusFlow: Record<string, { color: string; icon: string; label: string }> = {
  draft: { color: "bg-gray-100 text-gray-700", icon: "📝", label: "Draft" },
  pending_review: { color: "bg-yellow-100 text-yellow-700", icon: "👀", label: "In Review" },
  approved: { color: "bg-green-100 text-green-700", icon: "✅", label: "Approved" },
  published: { color: "bg-blue-100 text-blue-700", icon: "🚀", label: "Published" },
  rejected: { color: "bg-red-100 text-red-700", icon: "❌", label: "Rejected" },
};

export function ReleaseManagerPanel({ releases, onSubmit, onPublish }: {
  releases: Release[]; onSubmit?: (id: string) => void; onPublish?: (id: string) => void;
}) {
  return (
    <div className="space-y-2">
      <h3 className="font-bold text-sm">Releases</h3>
      {releases.map(r => {
        const cfg = statusFlow[r.status] || statusFlow.draft;
        return (
          <div key={r.releaseId} className="border dark:border-gray-700 rounded-xl p-3 space-y-2">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm">v{r.version}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${cfg.color}`}>{cfg.icon} {cfg.label}</span>
              </div>
              <div className="flex gap-1">
                {r.status === "draft" && <button onClick={() => onSubmit?.(r.releaseId)} className="text-xs bg-blue-500 text-white px-2 py-1 rounded-lg">Submit</button>}
                {r.status === "approved" && <button onClick={() => onPublish?.(r.releaseId)} className="text-xs bg-green-500 text-white px-2 py-1 rounded-lg">Publish</button>}
              </div>
            </div>
            <ul className="text-xs text-gray-500 ml-4">{r.changelog.map((c, i) => <li key={i}>• {c}</li>)}</ul>
            {r.reviewComment && <p className="text-xs bg-yellow-50 dark:bg-yellow-900/10 rounded p-2">💬 {r.reviewComment}</p>}
          </div>
        );
      })}
    </div>
  );
}
