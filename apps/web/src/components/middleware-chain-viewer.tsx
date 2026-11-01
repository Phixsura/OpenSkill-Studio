"use client";

interface MwStep { name: string; status: string; error?: string; }
interface MiddlewareChainViewerProps { steps: MwStep[]; completed: boolean; }

const STATUS_ICON: Record<string, string> = { applied: "✅", error: "❌", skipped: "⏭️" };

export function MiddlewareChainViewer({ steps, completed }: MiddlewareChainViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Middleware Chain</h3>
        <span className={`text-xs font-bold ${completed ? "text-green-600" : "text-red-500"}`}>
          {completed ? "✅ Complete" : "❌ Aborted"}
        </span>
      </div>
      <div className="p-4 flex items-center gap-1">
        {steps.map((s, i) => (
          <div key={s.name} className="flex items-center gap-1">
            <div className={`px-2 py-1 rounded text-xs ${s.status === "applied" ? "bg-green-100 dark:bg-green-900 text-green-700" : "bg-red-100 dark:bg-red-900 text-red-700"}`}>
              {STATUS_ICON[s.status] ?? "⏳"} {s.name}
            </div>
            {i < steps.length - 1 && <span className="text-gray-400">→</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
