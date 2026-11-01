"use client";

interface SurveyResult { text: string; type: string; count?: number; average?: number; counts?: Record<string, number>; }
interface NpsScore { nps: number; responses: number; promotersPct: number; detractorsPct: number; }

export function FeedbackSurveyPanel({ results, nps }: { results: Record<string, SurveyResult>; nps: NpsScore | null }) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📝 Feedback Survey</h2>
      {nps && (
        <div className="rounded-xl border dark:border-gray-700 p-4 text-center">
          <span className="text-xs text-gray-500 block">Net Promoter Score</span>
          <span className={`text-3xl font-bold ${nps.nps >= 50 ? "text-green-600" : nps.nps >= 0 ? "text-yellow-600" : "text-red-600"}`}>{nps.nps}</span>
          <div className="flex justify-center gap-4 mt-1 text-xs text-gray-500">
            <span className="text-green-600">{nps.promotersPct}% promoters</span>
            <span className="text-red-500">{nps.detractorsPct}% detractors</span>
            <span>{nps.responses} responses</span>
          </div>
        </div>
      )}
      <div className="space-y-2">
        {Object.entries(results).map(([id, r]) => (
          <div key={id} className="rounded-lg border dark:border-gray-700 p-3">
            <span className="font-semibold text-sm">{r.text}</span>
            {r.average !== undefined && <span className="text-sm text-blue-600 ml-2">avg: {r.average}</span>}
            {r.counts && (
              <div className="flex gap-2 mt-1 text-xs">{Object.entries(r.counts).map(([k, v]) => <span key={k}>{k}: <b>{v}</b></span>)}</div>
            )}
            {r.count !== undefined && r.type === "text" && <span className="text-xs text-gray-400 ml-2">{r.count} responses</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
