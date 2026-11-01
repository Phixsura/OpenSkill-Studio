"use client";

interface ResponseInfo { response_id: string; incident_type: string; status: string; current_step: number; total_steps: number; responder_count: number; }
interface Props { responses: ResponseInfo[]; appName: string; }

const sStyle: Record<string, string> = { idle: "bg-gray-100 text-gray-500 dark:bg-gray-800", activated: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300", mitigating: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300", resolved: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" };

export default function APIDeveloperAPIIncidentResponseCard({ responses, appName }: Props) {
  const active = responses.filter((r) => r.status === "activated" || r.status === "mitigating").length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚨 Incident Response</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{responses.length} playbooks</span>
          {active > 0 && <p className="text-[10px] text-red-500">{active} active</p>}
        </div>
      </div>
      {responses.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No incident responses</p>
      ) : (
        <div className="space-y-1.5">
          {responses.map((r) => (
            <div key={r.response_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${sStyle[r.status] ?? ""}`}>{r.status}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.incident_type}</span>
              </div>
              <span className="text-gray-400">step {r.current_step + 1}/{r.total_steps} · {r.responder_count} responders</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
