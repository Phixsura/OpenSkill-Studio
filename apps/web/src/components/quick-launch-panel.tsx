"use client";

interface QuickLaunchInfo {
  launchId: string; templateName: string; extensionName: string;
  status: string; progressPct: number; previewUrl: string; error: string;
}

const statusConfig: Record<string, { icon: string; color: string }> = {
  initializing: { icon: "⏳", color: "text-gray-500" },
  configuring: { icon: "⚙️", color: "text-blue-600" },
  deploying: { icon: "🚀", color: "text-purple-600" },
  live: { icon: "🟢", color: "text-green-600" },
  failed: { icon: "❌", color: "text-red-600" },
};

export function QuickLaunchPanel({ launch, onLaunch }: {
  launch: QuickLaunchInfo | null;
  onLaunch?: (template: string, name: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🚀 Quick Launch</h2>

      {!launch && (
        <div className="rounded-xl border dark:border-gray-700 p-6 text-center">
          <span className="text-4xl block mb-3">🎯</span>
          <p className="text-sm text-gray-500 mb-3">Launch an extension in one click</p>
          <button onClick={() => onLaunch?.("starter", "my-extension")}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-xl font-bold">
            Launch Now
          </button>
        </div>
      )}

      {launch && (
        <div className="rounded-xl border dark:border-gray-700 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span>{statusConfig[launch.status]?.icon}</span>
              <span className="font-bold">{launch.extensionName}</span>
              <span className={`text-sm capitalize ${statusConfig[launch.status]?.color}`}>{launch.status}</span>
            </div>
            <span className="text-sm font-bold">{launch.progressPct}%</span>
          </div>

          <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all ${launch.status === "live" ? "bg-green-500" : launch.status === "failed" ? "bg-red-500" : "bg-blue-500"}`}
              style={{ width: `${launch.progressPct}%` }} />
          </div>

          {launch.previewUrl && (
            <div className="text-xs text-blue-600">🌐 {launch.previewUrl}</div>
          )}
          {launch.error && <div className="text-xs text-red-500">⚠ {launch.error}</div>}
        </div>
      )}
    </div>
  );
}
