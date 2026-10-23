"use client";

interface Plan { id: string; price_label: string; apps_label: string; api_label: string; support: string; }
interface FeatureRow { feature: string; [planId: string]: unknown; }
interface PlanComparisonTableProps { plans: Plan[]; featureMatrix: FeatureRow[];
  onSelect: (planId: string) => void; recommendedPlan?: string; }

export function PlanComparisonTable({ plans, featureMatrix, onSelect, recommendedPlan }: PlanComparisonTableProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-center text-2xl font-bold">Compare Plans</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b dark:border-gray-700">
              <th className="pb-3 text-left"></th>
              {plans.map(p => (
                <th key={p.id} className="pb-3 text-center">
                  <p className={`text-lg font-bold capitalize ${p.id === recommendedPlan ? "text-blue-600" : ""}`}>
                    {p.id} {p.id === recommendedPlan && "⭐"}
                  </p>
                  <p className="text-xl font-black">{p.price_label}</p>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="border-b dark:border-gray-800">
              <td className="py-2 text-gray-500">Apps</td>
              {plans.map(p => <td key={p.id} className="py-2 text-center font-medium">{p.apps_label}</td>)}
            </tr>
            <tr className="border-b dark:border-gray-800">
              <td className="py-2 text-gray-500">API Calls</td>
              {plans.map(p => <td key={p.id} className="py-2 text-center font-medium">{p.api_label}</td>)}
            </tr>
            <tr className="border-b dark:border-gray-800">
              <td className="py-2 text-gray-500">Support</td>
              {plans.map(p => <td key={p.id} className="py-2 text-center capitalize">{p.support}</td>)}
            </tr>
            {featureMatrix.map(row => (
              <tr key={row.feature} className="border-b dark:border-gray-800">
                <td className="py-1.5 text-gray-500 capitalize">{String(row.feature).replace(/_/g, " ")}</td>
                {plans.map(p => (
                  <td key={p.id} className="py-1.5 text-center">
                    {row[p.id] ? <span className="text-green-500">✓</span> : <span className="text-gray-300">—</span>}
                  </td>
                ))}
              </tr>
            ))}
            <tr>
              <td></td>
              {plans.map(p => (
                <td key={p.id} className="pt-4 text-center">
                  <button onClick={() => onSelect(p.id)}
                    className={`rounded-lg px-4 py-2 text-sm font-semibold ${p.id === recommendedPlan ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
                    {p.price_label === "Free" ? "Get Started" : p.price_label === "Custom" ? "Contact Sales" : "Start Trial"}
                  </button>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
