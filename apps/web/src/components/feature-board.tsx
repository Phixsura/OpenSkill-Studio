"use client";

interface FeatureReq { title: string; status: string; votes: number; author: string; category: string; }
interface FeatureBoardProps { requests: FeatureReq[]; totalVotes: number; onVote: (title: string) => void; }

const statusColors: Record<string, string> = {
  open: "bg-blue-100 text-blue-700", under_review: "bg-yellow-100 text-yellow-700",
  planned: "bg-purple-100 text-purple-700", in_progress: "bg-orange-100 text-orange-700",
  completed: "bg-green-100 text-green-700", declined: "bg-gray-100 text-gray-500",
};

export function FeatureBoard({ requests, totalVotes, onVote }: FeatureBoardProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Feature Requests</h3>
        <span className="text-xs text-gray-400">{requests.length} requests · {totalVotes} votes</span>
      </div>
      <div className="space-y-2">
        {requests.map((r, i) => (
          <div key={i} className="flex items-center gap-3 rounded-lg border p-3 dark:border-gray-700">
            <button onClick={() => onVote(r.title)}
              className="flex flex-col items-center rounded border px-2 py-1 text-xs hover:bg-blue-50 dark:border-gray-600 dark:hover:bg-blue-900/10">
              <span>▲</span><span className="font-bold">{r.votes}</span>
            </button>
            <div className="flex-1">
              <p className="text-sm font-medium">{r.title}</p>
              <div className="mt-1 flex items-center gap-2">
                <span className={`rounded px-1.5 py-0.5 text-xs ${statusColors[r.status] ?? ""} dark:bg-opacity-30`}>{r.status.replace("_", " ")}</span>
                <span className="text-xs text-gray-400">by {r.author}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
