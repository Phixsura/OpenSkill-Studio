"use client";

interface PlatformSummary {
  totalExtensions: number;
  totalDevelopers: number;
  totalInstalls: number;
  totalServices: number;
  testsGreen: number;
  healthScore: number;
}

export function PlatformSummaryCard({ summary }: { summary: PlatformSummary }) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white text-center">
        <h1 className="text-2xl font-bold">🚀 OpenSkill Developer Platform</h1>
        <p className="text-sm opacity-80 mt-1">Extension SDK · Sandboxed Apps · Connector Marketplace · Automation API</p>
      </div>

      <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
        {[
          { label: "Extensions", value: summary.totalExtensions, icon: "📦" },
          { label: "Developers", value: summary.totalDevelopers, icon: "👩‍💻" },
          { label: "Installs", value: summary.totalInstalls.toLocaleString(), icon: "📥" },
          { label: "Services", value: summary.totalServices, icon: "⚙️" },
          { label: "Tests", value: summary.testsGreen.toLocaleString(), icon: "✅" },
          { label: "Health", value: `${summary.healthScore}%`, icon: "💚" },
        ].map((s) => (
          <div key={s.label} className="rounded-xl border dark:border-gray-700 p-3 text-center">
            <span className="text-xl block">{s.icon}</span>
            <span className="font-bold text-lg block">{s.value}</span>
            <span className="text-xs text-gray-500">{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
