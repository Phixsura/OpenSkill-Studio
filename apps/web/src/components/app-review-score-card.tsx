"use client";

interface ScoreBreakdown {
  name: string;
  score: number;
  weight: number;
  details: string;
}

interface ReviewScoreData {
  app_id: string;
  composite_score: number;
  grade: "excellent" | "good" | "fair" | "poor";
  breakdown: ScoreBreakdown[];
  auto_approve: boolean;
  flags: string[];
}

interface AppReviewScoreCardProps {
  score: ReviewScoreData;
  appName: string;
  onApprove: () => void;
  onReject: () => void;
}

const GRADE_STYLES: Record<string, { label: string; color: string; ring: string }> = {
  excellent: { label: "Excellent", color: "text-green-600", ring: "stroke-green-500" },
  good: { label: "Good", color: "text-blue-600", ring: "stroke-blue-500" },
  fair: { label: "Fair", color: "text-yellow-600", ring: "stroke-yellow-500" },
  poor: { label: "Poor", color: "text-red-600", ring: "stroke-red-500" },
};

function ScoreRing({ score, grade }: { score: number; grade: string }) {
  const r = 40;
  const c = 2 * Math.PI * r;
  const offset = c - (score / 100) * c;
  const style = GRADE_STYLES[grade] ?? GRADE_STYLES.poor;
  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="96" height="96" className="-rotate-90">
        <circle
          cx="48"
          cy="48"
          r={r}
          fill="none"
          strokeWidth="7"
          className="stroke-gray-200 dark:stroke-gray-700"
        />
        <circle
          cx="48"
          cy="48"
          r={r}
          fill="none"
          strokeWidth="7"
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={style.ring}
        />
      </svg>
      <div className="absolute text-center">
        <p className={`text-xl font-bold ${style.color}`}>{score}</p>
        <p className="text-[10px] text-gray-500">{style.label}</p>
      </div>
    </div>
  );
}

function barColor(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 60) return "bg-blue-500";
  if (score >= 40) return "bg-yellow-500";
  return "bg-red-500";
}

export function AppReviewScoreCard({
  score,
  appName,
  onApprove,
  onReject,
}: AppReviewScoreCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div>
          <h3 className="font-semibold">Review Score</h3>
          <p className="text-xs text-gray-500">{appName}</p>
        </div>
        <ScoreRing score={score.composite_score} grade={score.grade} />
      </div>

      {/* Auto-approve banner */}
      {score.auto_approve && (
        <div className="bg-green-50 px-4 py-2 text-xs font-medium text-green-700 dark:bg-green-900/10 dark:text-green-400">
          ✅ Eligible for auto-approval
        </div>
      )}

      {/* Flags */}
      {score.flags.length > 0 && (
        <div className="border-b border-gray-200 bg-yellow-50 px-4 py-2 dark:border-gray-700 dark:bg-yellow-900/10">
          <p className="text-[10px] font-semibold text-yellow-700 dark:text-yellow-300">
            ⚠ Review Flags
          </p>
          <ul className="mt-1 space-y-0.5">
            {score.flags.map((f, i) => (
              <li key={i} className="text-xs text-yellow-600 dark:text-yellow-400">
                • {f}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Breakdown */}
      <div className="px-4 py-3">
        <p className="text-[10px] font-semibold uppercase text-gray-400">Score Breakdown</p>
        <div className="mt-2 space-y-2">
          {score.breakdown.map((b) => (
            <div key={b.name}>
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium">{b.name}</span>
                <span className="text-gray-500">
                  {b.score.toFixed(0)}{" "}
                  <span className="text-gray-400">({(b.weight * 100).toFixed(0)}%)</span>
                </span>
              </div>
              <div className="mt-0.5 flex items-center gap-2">
                <div className="h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div
                    className={`h-full rounded-full ${barColor(b.score)}`}
                    style={{ width: `${Math.min(b.score, 100)}%` }}
                  />
                </div>
                <span className="w-20 text-right text-[10px] text-gray-400">{b.details}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-2 border-t border-gray-200 px-4 py-3 dark:border-gray-700">
        <button
          onClick={onReject}
          className="rounded-md border border-red-300 px-4 py-1.5 text-sm text-red-600 hover:bg-red-50 dark:border-red-700 dark:text-red-400"
        >
          Reject
        </button>
        <button
          onClick={onApprove}
          className="rounded-md bg-green-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-green-700"
        >
          Approve
        </button>
      </div>
    </div>
  );
}
