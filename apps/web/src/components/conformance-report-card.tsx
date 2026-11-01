"use client";

interface Check { name: string; status: string; message: string; }

interface ConformanceReportCardProps {
  appName: string;
  version: string;
  passed: boolean;
  checks: Check[];
  checkedAt: string;
}

export function ConformanceReportCard({ appName, version, passed, checks, checkedAt }: ConformanceReportCardProps) {
  const passCount = checks.filter(c => c.status === "pass").length;

  return (
    <div className={`rounded-lg border p-4 ${passed ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h4 className="font-semibold">{appName} v{version}</h4>
          <p className="text-xs text-gray-400">Checked {checkedAt}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-sm font-medium ${
          passed ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                 : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
        }`}>
          {passed ? "✅ Passed" : "❌ Failed"} ({passCount}/{checks.length})
        </span>
      </div>
      <ul className="space-y-1">
        {checks.map(c => (
          <li key={c.name} className="flex items-center gap-2 text-sm">
            <span>{c.status === "pass" ? "✅" : c.status === "warn" ? "⚠️" : "❌"}</span>
            <span className="font-medium">{c.name.replace(/_/g, " ")}</span>
            <span className="text-gray-500">— {c.message}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
