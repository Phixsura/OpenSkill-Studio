"use client";

interface ReviewHighlight { text: string; rating: number; }
interface ReviewReportCardProps { appName: string; period: string; total: number;
  avgRating: number; fiveStarCount: number; oneStarCount: number;
  responseRate: number; highlights: ReviewHighlight[]; concerns: ReviewHighlight[]; }

export function ReviewReportCard({ appName, period, total, avgRating, fiveStarCount,
  oneStarCount, responseRate, highlights, concerns }: ReviewReportCardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{appName} — Review Report</h2>
        <span className="text-xs text-gray-400">{period}</span>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center">
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{total}</p><p className="text-[10px] text-gray-400">Reviews</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">⭐ {avgRating}</p><p className="text-[10px] text-gray-400">Avg</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-green-600">{fiveStarCount}</p><p className="text-[10px] text-gray-400">5-Star</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{responseRate}%</p><p className="text-[10px] text-gray-400">Responded</p>
        </div>
      </div>
      {highlights.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-green-600">✨ Highlights</h3>
          {highlights.map((h, i) => (
            <p key={i} className="ml-4 text-xs text-gray-500">&ldquo;{h.text}&rdquo; — ⭐{h.rating}</p>
          ))}
        </div>
      )}
      {concerns.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-red-600">⚠️ Concerns</h3>
          {concerns.map((c, i) => (
            <p key={i} className="ml-4 text-xs text-gray-500">&ldquo;{c.text}&rdquo; — ⭐{c.rating}</p>
          ))}
        </div>
      )}
    </div>
  );
}
