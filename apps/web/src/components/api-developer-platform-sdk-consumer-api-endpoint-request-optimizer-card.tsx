"use client";

interface Suggestion { id: string; category: string; title: string; description: string; improvement: number; }
interface Props { suggestions: Suggestion[]; totalSavings: number; consumerId: string; appName: string; }

const catColors: Record<string, string> = { caching: "bg-blue-100 text-blue-700", batching: "bg-green-100 text-green-700", compression: "bg-purple-100 text-purple-700", pagination: "bg-amber-100 text-amber-700", reduction: "bg-red-100 text-red-700" };
const catIcons: Record<string, string> = { caching: "💾", batching: "📦", compression: "🗜️", pagination: "📄", reduction: "✂️" };

export default function APIDeveloperPlatformSDKConsumerApiEndpointRequestOptimizerCard({ suggestions, totalSavings, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Request Optimizer</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        {totalSavings > 0 && <span className="text-sm font-bold text-green-600">~{totalSavings}% savings</span>}
      </div>
      {suggestions.length === 0 ? (
        <p className="text-center text-sm text-green-500">✅ No optimizations needed!</p>
      ) : (
        <div className="space-y-2">
          {suggestions.map((s) => (
            <div key={s.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center gap-1 text-[11px]">
                <span>{catIcons[s.category] ?? "💡"}</span>
                <span className="font-medium text-gray-700 dark:text-gray-300">{s.title}</span>
                <span className={`ml-auto rounded px-1 py-0.5 text-[9px] ${catColors[s.category] ?? ""}`}>~{s.improvement}%</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-500">{s.description}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
