"use client";

interface Insight { type: string; icon: string; title: string; message: string; }
interface AppInsightsPanelProps { insights: Insight[]; }

const TYPE_STYLES: Record<string, string> = {
  positive: "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/10",
  warning: "border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/10",
  critical: "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/10",
  action: "border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/10",
};

export function AppInsightsPanel({ insights }: AppInsightsPanelProps) {
  if (insights.length === 0) return null;
  return (
    <div className="space-y-2">
      <h3 className="font-semibold">Insights</h3>
      {insights.map((insight, i) => (
        <div key={i} className={`rounded-lg border p-3 ${TYPE_STYLES[insight.type] || ""}`}>
          <div className="flex items-center gap-2">
            <span className="text-lg">{insight.icon}</span>
            <div>
              <p className="text-sm font-medium">{insight.title}</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">{insight.message}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
