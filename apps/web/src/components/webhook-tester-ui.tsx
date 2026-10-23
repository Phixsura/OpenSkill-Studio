"use client";

interface TestResult { success: boolean; statusCode: number; latencyMs: number;
  grade: string; issues: string[]; isJson: boolean; }
interface WebhookTesterUiProps { result: TestResult | null;
  onTest: (eventType: string) => void; testing: boolean; }

const GRADE_STYLE: Record<string, string> = {
  A: "bg-green-100 text-green-700", B: "bg-yellow-100 text-yellow-700", F: "bg-red-100 text-red-700",
};

export function WebhookTesterUi({ result, onTest, testing }: WebhookTesterUiProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🧪 Webhook Tester</h3>
      <button onClick={() => onTest("app.installed")} disabled={testing}
        className="w-full py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50 mb-3">
        {testing ? "Testing..." : "Send Test Event"}
      </button>
      {result && (
        <div className={`p-3 rounded-lg ${result.success ? "bg-green-50 dark:bg-green-900/20" : "bg-red-50 dark:bg-red-900/20"}`}>
          <div className="flex items-center justify-between mb-1">
            <span className={`text-sm font-bold ${result.success ? "text-green-700" : "text-red-700"}`}>
              {result.success ? "✅ Success" : "❌ Failed"}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${GRADE_STYLE[result.grade] || ""}`}>
              Grade: {result.grade}
            </span>
          </div>
          <div className="flex gap-3 text-xs text-gray-500">
            <span>HTTP {result.statusCode}</span>
            <span>{result.latencyMs}ms</span>
            <span>{result.isJson ? "JSON ✓" : "Not JSON"}</span>
          </div>
          {result.issues.length > 0 && (
            <div className="mt-1 text-xs text-red-500">{result.issues.join(" · ")}</div>
          )}
        </div>
      )}
    </div>
  );
}
