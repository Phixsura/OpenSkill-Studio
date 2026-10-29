"use client";

interface GuaranteeInfo { destination: string; guarantee_type: string; first_try_rate: number; overall_delivery_rate: number; guarantee_met: boolean; permanently_failed: number; }
interface Props { guarantees: GuaranteeInfo[]; unmetCount: number; appName: string; }

const gBadge: Record<string, string> = { at_least_once: "bg-blue-100 text-blue-700", at_most_once: "bg-yellow-100 text-yellow-700", exactly_once: "bg-purple-100 text-purple-700" };

export default function APIDeveloperPlatformSDKApiDeveloperApiWebhookDeliveryGuaranteeCard({ guarantees, unmetCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ Delivery Guarantees</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unmetCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{unmetCount} unmet</span>}
      </div>
      {guarantees.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No delivery guarantees</p>
      ) : (
        <div className="space-y-2">
          {guarantees.map((g) => (
            <div key={g.destination} className={`rounded-lg p-2 ${g.guarantee_met ? "bg-green-50 dark:bg-green-900/20" : "bg-red-50 dark:bg-red-900/20"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className={`rounded px-1 py-0.5 text-[9px] ${gBadge[g.guarantee_type] ?? ""}`}>{g.guarantee_type.replace(/_/g, " ")}</span>
                  <span className="text-gray-700 dark:text-gray-300">{new URL(g.destination).hostname}</span>
                </div>
                <span className={g.guarantee_met ? "text-green-600 font-bold" : "text-red-500 font-bold"}>{g.guarantee_met ? "✓ MET" : "✗ UNMET"}</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>1st try: {g.first_try_rate}%</span>
                <span>overall: {g.overall_delivery_rate}%</span>
                {g.permanently_failed > 0 && <span className="text-red-500">{g.permanently_failed} failed</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
