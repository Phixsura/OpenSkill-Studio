"use client";

interface CategoryResult { avg: number; responses: number; satisfied: number; }
interface DevSurveyResultsProps { respondents: number; overallSatisfaction: number;
  nps: number; categories: Record<string, CategoryResult>; }

export function DevSurveyResults({ respondents, overallSatisfaction, nps, categories }: DevSurveyResultsProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Developer Satisfaction</h3>
        <span className="text-xs text-gray-400">{respondents} responses</span>
      </div>
      <div className="grid grid-cols-2 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-2xl font-bold">⭐ {overallSatisfaction}</div>
          <div className="text-[10px] text-gray-400">Overall / 5</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className={`text-2xl font-bold ${nps >= 0 ? "text-green-600" : "text-red-500"}`}>{nps > 0 ? "+" : ""}{nps}</div>
          <div className="text-[10px] text-gray-400">NPS</div>
        </div>
      </div>
      <div className="p-3 space-y-2">
        {Object.entries(categories).map(([cat, data]) => (
          <div key={cat}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="capitalize">{cat}</span>
              <span className="text-gray-400">{data.avg}/5 · {data.satisfied}/{data.responses} satisfied</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${data.avg >= 4 ? "bg-green-500" : data.avg >= 3 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${data.avg * 20}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
