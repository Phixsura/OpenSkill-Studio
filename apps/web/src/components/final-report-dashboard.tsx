"use client";

interface FinalReportData {
  scale: { total: number; backend: number; frontend: number; tests: number; commits: number; security: number };
  quality: { passRate: number; dora: string };
  modules: string[];
  achievements: string[];
}

export function FinalReportDashboard({ report }: { report: FinalReportData }) {
  const isElite = report.quality.dora === "elite";

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className={`rounded-2xl p-8 text-white text-center ${isElite ? "bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500" : "bg-gradient-to-r from-blue-600 to-purple-600"}`}>
        <h1 className="text-3xl font-bold">🏆 OpenSkill Developer Platform</h1>
        <p className="text-lg mt-1">Extension SDK · Sandboxed Apps · Connector Marketplace</p>
        <p className="text-lg">Automation API · Third-party Ecosystem</p>
        <div className="mt-4 bg-white/20 rounded-full px-6 py-2 inline-block">
          <span className="text-xl font-bold uppercase">{report.quality.dora} Performance</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
        {[
          { l: "Services", v: report.scale.total, i: "⚙️" },
          { l: "Backend", v: report.scale.backend, i: "🔧" },
          { l: "Frontend", v: report.scale.frontend, i: "🎨" },
          { l: "Tests", v: report.scale.tests.toLocaleString(), i: "✅" },
          { l: "Commits", v: report.scale.commits.toLocaleString(), i: "📝" },
          { l: "Security", v: report.scale.security, i: "🛡️" },
        ].map((m) => (
          <div key={m.l} className="rounded-xl border dark:border-gray-700 p-3 text-center">
            <span className="text-2xl block">{m.i}</span>
            <span className="font-bold text-lg block">{m.v}</span>
            <span className="text-xs text-gray-500">{m.l}</span>
          </div>
        ))}
      </div>

      <div>
        <h3 className="text-sm font-bold mb-2">🏆 Achievements ({report.achievements.length})</h3>
        <div className="flex flex-wrap gap-2">
          {report.achievements.map((a) => (
            <span key={a} className="text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 px-3 py-1.5 rounded-full font-medium">{a}</span>
          ))}
        </div>
      </div>

      <div className="text-center text-xs text-gray-500 py-4 border-t dark:border-gray-700">
        <p>All {report.scale.total} services aligned to Issue #44 · {report.quality.passRate}% test pass rate · DORA {report.quality.dora}</p>
      </div>
    </div>
  );
}
