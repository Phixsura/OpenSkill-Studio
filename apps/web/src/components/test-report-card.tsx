"use client";

interface TestReportCardProps { appName: string; passRate: number; passed: number; failed: number; generatedAt: string; }

export function TestReportCard({ appName, passRate, passed, failed, generatedAt }: TestReportCardProps) {
  const color = passRate === 100 ? "green" : passRate >= 80 ? "yellow" : "red";
  const colors = { green: "bg-green-100 text-green-800", yellow: "bg-yellow-100 text-yellow-800", red: "bg-red-100 text-red-800" };

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{appName} — Test Report</h3>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${colors[color]}`}>{passRate}%</span>
      </div>
      <div className="mt-3 flex gap-4 text-sm">
        <span className="text-green-600">✅ {passed} passed</span>
        <span className={failed > 0 ? "text-red-600" : "text-gray-400"}>❌ {failed} failed</span>
      </div>
      <p className="mt-2 text-xs text-gray-400">Generated {new Date(generatedAt).toLocaleString()}</p>
    </div>
  );
}
