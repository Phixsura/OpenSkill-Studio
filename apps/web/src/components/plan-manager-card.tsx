"use client";

interface PlanInfo {
  plan_id: string;
  name: string;
  features: string[];
  price_cents: number;
  isCurrent: boolean;
}

interface PlanManagerCardProps {
  plans: PlanInfo[];
  appName: string;
}

function formatPrice(cents: number): string {
  if (cents === 0) return "Free";
  return `$${(cents / 100).toFixed(0)}/mo`;
}

const PLAN_ACCENTS: Record<number, string> = {
  0: "border-gray-300 dark:border-gray-600",
  1: "border-blue-400 dark:border-blue-500",
  2: "border-purple-400 dark:border-purple-500",
  3: "border-yellow-400 dark:border-yellow-500",
};

export default function PlanManagerCard({ plans, appName }: PlanManagerCardProps) {
  const current = plans.find((p) => p.isCurrent);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Plans</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {current && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
            {current.name}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
        {plans.map((p, i) => (
          <div
            key={p.plan_id}
            className={`rounded-lg border-2 px-3 py-3 ${PLAN_ACCENTS[i] ?? PLAN_ACCENTS[0]} ${p.isCurrent ? "bg-blue-50/50 dark:bg-blue-950/20" : ""}`}
          >
            <div className="mb-1 flex items-center justify-between">
              <span className="text-sm font-bold text-gray-800 dark:text-gray-200">{p.name}</span>
              <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                {formatPrice(p.price_cents)}
              </span>
            </div>
            {p.isCurrent && (
              <p className="mb-1.5 text-[10px] text-blue-600 dark:text-blue-400">Current plan</p>
            )}
            <ul className="space-y-0.5">
              {p.features.map((f) => (
                <li
                  key={f}
                  className="flex items-center gap-1 text-[11px] text-gray-600 dark:text-gray-400"
                >
                  <span className="text-green-500">✓</span> {f}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
