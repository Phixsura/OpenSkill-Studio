"use client";

interface ErrorGroup { fingerprint: string; errorType: string; message: string; count: number; lastSeen: number; resolved: boolean; }

export function ErrorTrackingDashboard({ groups, onResolve }: {
  groups: ErrorGroup[]; onResolve?: (fingerprint: string) => void;
}) {
  if (!groups.length) return <div className="text-center text-green-600 py-6"><span className="text-2xl block">✅</span><span className="text-sm font-medium mt-1 block">No unresolved errors</span></div>;
  const totalErrors = groups.reduce((sum, g) => sum + g.count, 0);

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <span className="font-bold text-sm">Errors ({totalErrors} total)</span>
        <span className="text-xs text-gray-500">{groups.length} groups</span>
      </div>
      {groups.map(g => (
        <div key={g.fingerprint} className="border border-red-200 dark:border-red-800 rounded-xl p-3 bg-red-50 dark:bg-red-900/10">
          <div className="flex justify-between items-start">
            <div>
              <span className="font-mono text-xs text-red-600 dark:text-red-400 font-bold">{g.errorType}</span>
              <span className="text-xs bg-red-200 dark:bg-red-800 text-red-700 dark:text-red-300 px-1.5 rounded ml-2">{g.count}×</span>
              <p className="text-sm mt-0.5">{g.message}</p>
            </div>
            <button onClick={() => onResolve?.(g.fingerprint)} className="text-xs bg-green-500 text-white px-2 py-1 rounded-lg shrink-0">Resolve</button>
          </div>
        </div>
      ))}
    </div>
  );
}
