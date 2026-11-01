"use client";

interface Plan { id: string; name: string; priceCents: number; features: string[]; requestLimit: number; rps: number; }
interface Sub { planId: string; status: string; trialEndsAt: string | null; }
interface Props { plans: Plan[]; currentSub: Sub | null; consumerId: string; appName: string; }

const fmtPrice = (c: number) => c === 0 ? "Free" : `$${(c / 100).toFixed(2)}/mo`;

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiSubscriptionPlanCard({ plans, currentSub, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💳 Subscription Plans</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}{currentSub ? ` · ${currentSub.status}` : ""}</p>
      </div>
      {plans.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No plans available</p>
      ) : (
        <div className="space-y-2">
          {plans.map((p) => (
            <div key={p.id} className={`rounded-lg p-2 ${currentSub?.planId === p.id ? "border border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-900/20" : "bg-gray-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-semibold text-gray-700 dark:text-gray-300">{p.name}{currentSub?.planId === p.id ? " ✓" : ""}</span>
                <span className="font-bold text-gray-900 dark:text-gray-100">{fmtPrice(p.priceCents)}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">{p.requestLimit.toLocaleString()} req · {p.rps} rps</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
