"use client";

interface ReviewItem { appName: string; developer: string; submittedAt: string; stage: string; }
interface ReviewQueueBoardProps { stages: Record<string, ReviewItem[]>;
  pendingCount: number; onAdvance: (appName: string) => void; }

const STAGE_LABEL: Record<string, string> = {
  submitted: "📥 Submitted", automated_scan: "🤖 Auto Scan",
  manual_review: "👀 Manual Review", approved: "✅ Approved", rejected: "❌ Rejected",
};

export function ReviewQueueBoard({ stages, pendingCount, onAdvance }: ReviewQueueBoardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Review Queue</h3>
        <span className="text-xs text-gray-400">{pendingCount} pending</span>
      </div>
      <div className="grid grid-cols-5 gap-px bg-gray-200 dark:bg-gray-700">
        {Object.entries(stages).map(([stage, items]) => (
          <div key={stage} className="bg-white dark:bg-gray-900 p-2 min-h-[120px]">
            <p className="text-xs font-medium mb-2">{STAGE_LABEL[stage] || stage}</p>
            {items.map(item => (
              <div key={item.appName} className="text-xs bg-gray-50 dark:bg-gray-800 rounded p-1.5 mb-1 cursor-pointer hover:bg-blue-50"
                   onClick={() => onAdvance(item.appName)}>
                <p className="font-medium truncate">{item.appName}</p>
                <p className="text-gray-400">{item.developer}</p>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
