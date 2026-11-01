"use client";

interface FrameworkInfo { framework: string; total_controls: number; compliance_pct: number; assessment_pct: number; audit_ready: boolean; }
interface Props { frameworks: FrameworkInfo[]; overallCompliance: number; auditReadyCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperApiApiPlatformAuditComplianceCard({ frameworks, overallCompliance, auditReadyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Audit Compliance</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {overallCompliance}% overall</p>
        </div>
        <span className="rounded-full bg-green-100 px-2 py-0.5 text-[10px] text-green-700">{auditReadyCount} audit ready</span>
      </div>
      {frameworks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No compliance frameworks</p>
      ) : (
        <div className="space-y-2">
          {frameworks.map((f) => (
            <div key={f.framework} className={`rounded-lg p-2 ${f.audit_ready ? "bg-green-50 dark:bg-green-900/20" : "bg-gray-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-bold text-gray-700 dark:text-gray-300">{f.framework}</span>
                <span className={f.audit_ready ? "text-green-600 font-bold" : "text-gray-400"}>{f.compliance_pct}% compliant</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{f.total_controls} controls · {f.assessment_pct}% assessed</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
