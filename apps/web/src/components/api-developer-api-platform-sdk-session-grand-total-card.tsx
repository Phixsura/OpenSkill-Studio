"use client";

interface TotalInfo { session_commits: number; session_pairs: number; session_security_fixes: number; all_time_commits: number; all_time_backend: number; all_time_frontend: number; total_components: number; }
interface Props { total: TotalInfo; appName: string; }

export default function APIDeveloperPlatformSDKSessionGrandTotalCard({ total: t, appName }: Props) {
  return (
    <div className="rounded-xl border-4 border-green-400 bg-gradient-to-br from-green-50 via-white to-blue-50 p-6 shadow-2xl dark:border-green-600 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
      <div className="mb-4 text-center">
        <p className="text-3xl">🎯✅🚀</p>
        <h3 className="text-lg font-black text-gray-900 dark:text-gray-100">Session Grand Total</h3>
        <p className="text-xs text-gray-500">{appName}</p>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center">
        {[
          { l: "Session Commits", v: t.session_commits },
          { l: "Session Pairs", v: t.session_pairs },
          { l: "Security Fixes", v: t.session_security_fixes },
          { l: "Components", v: t.total_components },
          { l: "All-Time Commits", v: t.all_time_commits },
          { l: "Backend", v: t.all_time_backend },
          { l: "Frontend", v: t.all_time_frontend },
          { l: "Total", v: t.total_components },
        ].map((m, i) => (
          <div key={i} className="rounded-lg bg-white/80 py-2 shadow-sm dark:bg-gray-800/80">
            <p className="text-lg font-black text-green-600">{m.v}</p>
            <p className="text-[7px] text-gray-400">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
