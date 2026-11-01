"use client";

interface WebhookTestResultProps { success: boolean; statusCode: number | null; durationMs: number; verdict: string; responsePreview: string; }

export function WebhookTestResult({ success, statusCode, durationMs, verdict, responsePreview }: WebhookTestResultProps) {
  return (
    <div className={`rounded-lg border p-4 ${success ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20" : "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20"}`}>
      <p className="font-semibold">{verdict}</p>
      <div className="mt-2 flex gap-4 text-sm text-gray-600">
        {statusCode && <span>HTTP {statusCode}</span>}
        <span>{durationMs}ms</span>
      </div>
      {responsePreview && <pre className="mt-2 max-h-24 overflow-auto rounded bg-gray-100 p-2 text-xs dark:bg-gray-800">{responsePreview}</pre>}
    </div>
  );
}
