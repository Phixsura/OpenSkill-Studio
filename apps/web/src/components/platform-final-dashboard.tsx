"use client";

interface Summary {
  scale: { services: number; backend: number; frontend: number; tests: number; commits: number; securityFixes: number };
  quality: { testPassRate: number; uptime: number; errorRate: number; avgResponseMs: number };
  growth: { developers: number; extensions: number; installs: number; mrrCents: number };
  dora: string;
}

export function PlatformFinalDashboard({ summary, achievements }: {
  summary: Summary; achievements: string[];
}) {
  const isElite = summary.dora === "elite";
  return (
    <div className="space-y-6">
      <div className={`rounded-2xl p-8 text-white text-center ${isElite ? "bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500" : "bg-gradient-to-r from-blue-600 to-purple-600"}`}>
        <h1 className="text-3xl font-bold">🚀 OpenSkill Developer Platform</h1>
        <p className="text-lg mt-1 opacity-90">Extension SDK · Sandboxed Apps · Connector Marketplace · Automation API</p>
        <span className="inline-block mt-3 bg-white/20 rounded-full px-6 py-2 text-sm font-bold uppercase">{summary.dora} Performance</span>
      </div>

      <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
        {[
          { l: "Services", v: summary.scale.services, i: "⚙️" },
          { l: "Backend", v: summary.scale.backend, i: "🔧" },
          { l: "Frontend", v: summary.scale.frontend, i: "🎨" },
          { l: "Tests", v: summary.scale.tests.toLocaleString(), i: "✅" },
          { l: "Commits", v: summary.scale.commits.toLocaleString(), i: "📝" },
          { l: "Sec Fixes", v: summary.scale.securityFixes, i: "🛡️" },
        ].map((m) => (
          <div key={m.l} className="rounded-xl border dark:border-gray-700 p-3 text-center">
            <span className="text-2xl block">{m.i}</span>
            <span className="font-bold text-lg block">{m.v}</span>
            <span className="text-xs text-gray-500">{m.l}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-4 gap-2 text-center">
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block">Pass Rate</span>
          <span className="text-xl font-bold text-green-600">{summary.quality.testPassRate}%</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block">Uptime</span>
          <span className="text-xl font-bold text-green-600">{summary.quality.uptime}%</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block">Error Rate</span>
          <span className="text-xl font-bold text-green-600">{summary.quality.errorRate}%</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block">Latency</span>
          <span className="text-xl font-bold">{summary.quality.avgResponseMs}ms</span>
        </div>
      </div>

      {achievements.length > 0 && (
        <div>
          <h3 className="text-sm font-bold mb-2">🏆 Achievements Unlocked</h3>
          <div className="flex flex-wrap gap-2">
            {achievements.map((a) => (
              <span key={a} className="text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 px-3 py-1.5 rounded-full font-medium">{a}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
