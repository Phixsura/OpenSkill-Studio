"use client";

interface VersionInfo { name: string; current: string; latest: string;
  upToDate: boolean; updateType: string | null; }
interface VersionUpdateCheckerProps { components: VersionInfo[];
  updatesAvailable: number; allCurrent: boolean; }

const UPDATE_BADGE: Record<string, string> = {
  major: "bg-red-100 text-red-700", minor: "bg-yellow-100 text-yellow-700",
  patch: "bg-blue-100 text-blue-700",
};

export function VersionUpdateChecker({ components, updatesAvailable, allCurrent }: VersionUpdateCheckerProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">📦 Dependencies</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full ${allCurrent ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
          {allCurrent ? "✅ All current" : `${updatesAvailable} updates`}
        </span>
      </div>
      <div className="space-y-2">
        {components.map(c => (
          <div key={c.name} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
            <span className="text-sm font-medium">{c.name}</span>
            <div className="flex items-center gap-2 text-xs">
              <span className="font-mono">{c.current}</span>
              {!c.upToDate && (
                <>
                  <span className="text-gray-300">→</span>
                  <span className="font-mono font-bold">{c.latest}</span>
                  <span className={`px-1.5 py-0.5 rounded ${UPDATE_BADGE[c.updateType || ""] || ""}`}>{c.updateType}</span>
                </>
              )}
              {c.upToDate && <span className="text-green-600">✓</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
