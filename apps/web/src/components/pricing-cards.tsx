"use client";

interface PricingPlan { id: string; priceDisplay: string; apiCalls: number;
  apps: number; teamSize: number; features: string[]; isUnlimited: boolean; }
interface PricingCardsProps { plans: PricingPlan[]; currentPlan: string;
  onSelect: (planId: string) => void; }

export function PricingCards({ plans, currentPlan, onSelect }: PricingCardsProps) {
  return (
    <div className="grid grid-cols-4 gap-4">
      {plans.map(p => (
        <div key={p.id} className={`rounded-xl border p-5 ${
          p.id === currentPlan ? "border-blue-500 ring-2 ring-blue-200" : "dark:border-gray-700"
        }`}>
          <h3 className="font-bold capitalize mb-1">{p.id}</h3>
          <p className="text-2xl font-bold mb-3">{p.priceDisplay}</p>
          <ul className="text-xs text-gray-500 space-y-1 mb-4">
            <li>{p.isUnlimited ? "Unlimited" : p.apiCalls.toLocaleString()} API calls</li>
            <li>{p.isUnlimited ? "Unlimited" : p.apps} apps</li>
            <li>{p.isUnlimited ? "Unlimited" : p.teamSize} team members</li>
          </ul>
          <div className="text-xs text-gray-400 mb-3">{p.features.length} features</div>
          <button onClick={() => onSelect(p.id)}
            className={`w-full py-2 text-sm rounded-lg font-medium ${
              p.id === currentPlan ? "bg-gray-200 text-gray-500" : "bg-blue-600 text-white hover:bg-blue-700"
            }`}>{p.id === currentPlan ? "Current Plan" : "Select"}</button>
        </div>
      ))}
    </div>
  );
}
