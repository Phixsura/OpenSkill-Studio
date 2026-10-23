"use client";

interface FeatureReq { id: number; title: string; votes: number; status: string; category: string; }
interface FeatureRequestBoardProps { requests: FeatureReq[]; totalVotes: number;
  onVote: (id: number) => void; }

export function FeatureRequestBoard({ requests, totalVotes, onVote }: FeatureRequestBoardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💡 Feature Requests</h3>
        <span className="text-xs text-gray-400">{totalVotes} votes</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {requests.map(r => (
          <div key={r.id} className="flex items-center gap-3 px-4 py-3">
            <button onClick={() => onVote(r.id)}
              className="flex flex-col items-center w-12 shrink-0 py-1 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/20">
              <span className="text-xs">▲</span>
              <span className="text-sm font-bold">{r.votes}</span>
            </button>
            <div>
              <p className="text-sm font-medium">{r.title}</p>
              <div className="flex gap-2 text-xs text-gray-400">
                <span className="capitalize">{r.category}</span>
                <span className={r.status === "open" ? "text-green-600" : "text-gray-400"}>{r.status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
