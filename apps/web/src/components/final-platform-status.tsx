"use client";

interface FinalPlatformStatusProps { grade: string; score: number; commits: number;
  lines: number; files: number; modules: number; uptime: number; nps: number; }

export function FinalPlatformStatus({ grade, score, commits, lines, files, modules, uptime, nps }: FinalPlatformStatusProps) {
  return (
    <div className="rounded-xl border-2 border-green-500 overflow-hidden bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10">
      <div className="p-6 text-center">
        <div className="text-5xl font-bold text-green-600">{grade}</div>
        <div className="text-lg font-mono">{score}/100</div>
        <div className="text-sm text-gray-500 mt-1">OpenSkill Developer Platform</div>
        <div className="mt-2 inline-block px-4 py-1 bg-green-500 text-white rounded-full text-xs font-bold">✅ FULLY OPERATIONAL</div>
      </div>
      <div className="grid grid-cols-4 gap-px bg-green-200 dark:bg-green-800">
        {[{ l: "Commits", v: commits.toLocaleString() }, { l: "Lines", v: `${(lines/1000).toFixed(0)}K` },
          { l: "Files", v: files.toLocaleString() }, { l: "Modules", v: modules }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm font-bold text-green-700">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
