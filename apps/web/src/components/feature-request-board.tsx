"use client";

interface FeatureRequest { id: number; title: string; category: string; votes: number; status: string; }
interface FeatureRequestBoardProps { requests: FeatureRequest[]; total: number;
  openCount: number; onVote: (id: number) => void; }

export function FeatureRequestBoard({ requests, total, openCount, onVote }: FeatureRequestBoardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💡 Feature Requests</h3>
        <span className="text-xs text-gray-400">{openCount} open / {total} total</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {requests.map(r => (
          <div key={r.id} className="flex items-center gap-3 px-4 py-3">
            <button onClick={() => onVote(r.id)}
              className="flex flex-col items-center px-2 py-1 rounded border dark:border-gray-600 hover:bg-blue-50 dark:hover:bg-blue-900/10 min-w-[40px]">
              <span className="text-xs">▲</span>
              <span className="text-sm font-bold">{r.votes}</span>
            </button>
            <div className="flex-1">
              <div className="text-sm font-medium">{r.title}</div>
              <div className="text-[10px] text-gray-400">{r.category} · {r.status}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
