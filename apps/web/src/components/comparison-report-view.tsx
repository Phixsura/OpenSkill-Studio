"use client";

interface Metric { a: number; b: number; winner: string; }
interface ComparisonReportViewProps {
  appA: string; appB: string; metrics: Record<string, Metric>;
  recommendation: string; sharedPermissions: string[];
}

export function ComparisonReportView({ appA, appB, metrics, recommendation, sharedPermissions }: ComparisonReportViewProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="mb-3 font-semibold">{appA} vs {appB}</h3>
      <table className="mb-3 w-full text-sm">
        <thead><tr className="border-b"><th className="py-1 text-left">Metric</th><th className="text-right">{appA}</th><th className="text-right">{appB}</th><th className="text-center">Winner</th></tr></thead>
        <tbody>{Object.entries(metrics).map(([name, m]) => (
          <tr key={name} className="border-b dark:border-gray-800">
            <td className="py-1 capitalize">{name.replace(/_/g, " ")}</td>
            <td className={`text-right ${m.winner === "a" ? "font-bold text-green-600" : ""}`}>{m.a}</td>
            <td className={`text-right ${m.winner === "b" ? "font-bold text-green-600" : ""}`}>{m.b}</td>
            <td className="text-center">{m.winner === "tie" ? "=" : m.winner === "a" ? "←" : "→"}</td>
          </tr>
        ))}</tbody>
      </table>
      <p className="mb-2 text-sm font-medium">💡 {recommendation}</p>
      {sharedPermissions.length > 0 && (
        <div className="flex flex-wrap gap-1">
          <span className="text-xs text-gray-500">Shared:</span>
          {sharedPermissions.map(p => <span key={p} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{p}</span>)}
        </div>
      )}
    </div>
  );
}
