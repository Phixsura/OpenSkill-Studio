"use client";

interface WebhookHeadersViewerProps { headers: Record<string, string>; verified: boolean; }

export function WebhookHeadersViewer({ headers, verified }: WebhookHeadersViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 border-b dark:border-gray-700">
        <h4 className="text-sm font-semibold">📋 Request Headers</h4>
        <span className={`text-xs px-2 py-0.5 rounded-full ${verified ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
          {verified ? "✅ Verified" : "❌ Invalid"}
        </span>
      </div>
      <div className="p-3 font-mono text-xs space-y-0.5 bg-gray-900 text-gray-300">
        {Object.entries(headers).map(([k, v]) => (
          <div key={k}><span className="text-blue-400">{k}</span>: <span className="text-green-400">{v}</span></div>
        ))}
      </div>
    </div>
  );
}
