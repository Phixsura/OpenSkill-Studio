"use client";

interface AppScore { id: string; name: string; score: number; }
interface ComparisonResultCardProps { apps: AppScore[]; winner: AppScore; shareableUrl: string; onShare: () => void; }

export function ComparisonResultCard({ apps, winner, shareableUrl, onShare }: ComparisonResultCardProps) {
  const maxScore = Math.max(...apps.map(a => a.score), 1);
  return (
    <div className="rounded-lg border border-gray-200 p-6 dark:border-gray-700">
      <div className="text-center">
        <span className="text-3xl">🏆</span>
        <h2 className="mt-2 text-xl font-bold">{winner.name} wins!</h2>
        <p className="text-sm text-gray-400">Score: {winner.score}</p>
      </div>
      <div className="mt-4 space-y-2">
        {apps.map((a, i) => {
          const pct = Math.round((a.score / maxScore) * 100);
          return (
            <div key={a.id}>
              <div className="flex justify-between text-sm">
                <span className={a.id === winner.id ? "font-bold" : ""}>{a.name}</span>
                <span className="text-gray-400">{a.score}</span>
              </div>
              <div className="mt-0.5 h-3 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className={`h-full rounded-full ${a.id === winner.id ? "bg-green-500" : "bg-blue-400"}`}
                  style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
      <button onClick={onShare} className="mt-4 w-full rounded bg-blue-600 py-2 text-sm text-white">
        Share Comparison
      </button>
    </div>
  );
}
