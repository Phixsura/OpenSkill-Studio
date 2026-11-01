"use client";

interface ImpactReport {
  hoursSaved: number; errorsPrevented: number; tasksAutomated: number;
  usersImpacted: number; costSavings: number; productivityGain: number;
  annualHoursSaved: number; annualSavings: number;
}

function fmt(cents: number) { return `$${(cents / 100).toLocaleString()}`; }

export function ImpactReportPanel({ report, extensionName }: {
  report: ImpactReport; extensionName: string;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📊 {extensionName} Impact</h2>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-2xl font-bold text-blue-600">{report.hoursSaved}</span>
          <span className="text-xs text-gray-500 block">hrs/month saved</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-2xl font-bold text-green-600">{report.errorsPrevented}</span>
          <span className="text-xs text-gray-500 block">errors prevented</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-2xl font-bold text-purple-600">{report.tasksAutomated}</span>
          <span className="text-xs text-gray-500 block">tasks automated</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-2xl font-bold text-yellow-600">{fmt(report.costSavings)}</span>
          <span className="text-xs text-gray-500 block">monthly savings</span>
        </div>
      </div>

      <div className="rounded-xl bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-800 p-4 text-center">
        <span className="text-xs text-gray-500 block">Annual Impact</span>
        <div className="flex justify-center gap-6 mt-1">
          <div><span className="text-xl font-bold">{report.annualHoursSaved}h</span><span className="text-xs text-gray-500 block">saved</span></div>
          <div><span className="text-xl font-bold text-green-600">{fmt(report.annualSavings)}</span><span className="text-xs text-gray-500 block">saved</span></div>
          {report.productivityGain > 0 && (
            <div><span className="text-xl font-bold text-blue-600">+{report.productivityGain}%</span><span className="text-xs text-gray-500 block">productivity</span></div>
          )}
        </div>
      </div>
    </div>
  );
}
