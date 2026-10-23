"use client";

interface Control { id: string; name: string; status: string; notes: string; }
interface Section { category: string; controls: Control[]; count: number; }
interface ComplianceReportViewerProps { framework: string; organization: string;
  period: string; scoreDisplay: string; verdict: string; passed: number;
  failed: number; sections: Section[]; }

const STATUS_ICON: Record<string, string> = { passed: "✅", failed: "❌", "n/a": "⬜", pending: "⏳" };

export function ComplianceReportViewer({ framework, organization, period,
  scoreDisplay, verdict, passed, failed, sections }: ComplianceReportViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-5 border-b dark:border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-bold">{framework} Compliance Report</h3>
          <span className={`text-sm px-3 py-1 rounded-full font-medium ${
            verdict === "compliant" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
          }`}>{verdict === "compliant" ? "✅ Compliant" : "❌ Non-Compliant"}</span>
        </div>
        <div className="flex gap-4 text-sm text-gray-400">
          <span>{organization}</span><span>{period}</span>
          <span>Score: <strong>{scoreDisplay}</strong></span>
          <span className="text-green-600">{passed} passed</span>
          {failed > 0 && <span className="text-red-500">{failed} failed</span>}
        </div>
      </div>
      {sections.map(s => (
        <div key={s.category} className="border-b last:border-0 dark:border-gray-700">
          <div className="px-5 py-2 bg-gray-50 dark:bg-gray-800 text-xs font-semibold text-gray-400 uppercase">
            {s.category} ({s.count})
          </div>
          {s.controls.map(c => (
            <div key={c.id} className="flex items-center justify-between px-5 py-2 text-sm">
              <div className="flex items-center gap-2">
                <span>{STATUS_ICON[c.status] || "⏳"}</span>
                <span className="font-mono text-xs text-gray-400">{c.id}</span>
                <span>{c.name}</span>
              </div>
              {c.notes && <span className="text-xs text-gray-400">{c.notes}</span>}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
