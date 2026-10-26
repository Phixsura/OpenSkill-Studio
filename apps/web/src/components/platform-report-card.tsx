"use client";

interface PlatformReport {
  platform: { services: number; backend: number; frontend: number; tests: number; commits: number };
  quality: { testPassRate: number; avgLatencyMs: number; errorRate: number; uptime: number };
  growth: { developers: number; extensions: number; installs: number };
  dora: { classification: string; deploymentFrequency: string; leadTime: string; changeFailure: string; timeToRestore: string };
}

export function PlatformReportCard({ report }: { report: PlatformReport }) {
  const isElite = report.dora.classification === "elite";
  return (
    <div className="space-y-4">
      <div className={`rounded-xl p-6 text-white text-center ${isElite ? "bg-gradient-to-r from-yellow-500 to-orange-500" : "bg-gradient-to-r from-blue-600 to-purple-600"}`}>
        <h1 className="text-2xl font-bold">🏆 Platform Report</h1>
        <span className="text-lg font-bold uppercase">{report.dora.classification} Performance</span>
      </div>

      <div className="grid grid-cols-5 gap-2 text-center text-xs">
        {[
          { l: "Services", v: report.platform.services, i: "⚙️" },
          { l: "Backend", v: report.platform.backend, i: "🔧" },
          { l: "Frontend", v: report.platform.frontend, i: "🎨" },
          { l: "Tests", v: report.platform.tests.toLocaleString(), i: "✅" },
          { l: "Commits", v: report.platform.commits.toLocaleString(), i: "📝" },
        ].map((m) => (
          <div key={m.l} className="rounded-lg border dark:border-gray-700 p-2">
            <span className="block">{m.i}</span>
            <span className="font-bold text-sm">{m.v}</span>
            <span className="text-gray-500 block">{m.l}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Pass Rate</span>
          <span className="font-bold text-green-600">{report.quality.testPassRate}%</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Latency</span>
          <span className="font-bold">{report.quality.avgLatencyMs}ms</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Error Rate</span>
          <span className="font-bold text-green-600">{report.quality.errorRate}%</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Uptime</span>
          <span className="font-bold text-green-600">{report.quality.uptime}%</span>
        </div>
      </div>
    </div>
  );
}
