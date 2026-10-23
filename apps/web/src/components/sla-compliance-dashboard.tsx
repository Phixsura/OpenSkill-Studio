"use client";

interface SlaMetric { metric: string; target: number; actual: number; met: boolean; }
interface ServiceSla { service: string; compliant: boolean; metrics: SlaMetric[]; overall_score: number; }
interface SlaComplianceDashboardProps { period: string; services: ServiceSla[]; complianceRate: number; }

export function SlaComplianceDashboard({ period, services, complianceRate }: SlaComplianceDashboardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">SLA Compliance</h2>
        <span className="text-sm text-gray-400">{period}</span>
      </div>
      <div className="rounded-lg bg-gray-50 p-4 text-center dark:bg-gray-800">
        <p className={`text-3xl font-bold ${complianceRate >= 90 ? "text-green-600" : complianceRate >= 70 ? "text-yellow-600" : "text-red-600"}`}>
          {complianceRate}%
        </p>
        <p className="text-sm text-gray-400">Overall Compliance</p>
      </div>
      <div className="space-y-2">
        {services.map(svc => (
          <div key={svc.service} className="rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <span className="font-medium">{svc.service}</span>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${svc.compliant ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"}`}>
                {svc.compliant ? "Compliant" : "Violated"}
              </span>
            </div>
            <div className="mt-2 flex gap-3">
              {svc.metrics.map(m => (
                <div key={m.metric} className="text-xs">
                  <span className="text-gray-400">{m.metric}: </span>
                  <span className={m.met ? "text-green-600" : "text-red-600"}>{m.actual}</span>
                  <span className="text-gray-300"> / {m.target}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
