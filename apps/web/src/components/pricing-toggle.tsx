"use client";

interface PricingToggleProps { interval: "monthly" | "yearly"; onToggle: (interval: "monthly" | "yearly") => void; savingsPct?: number; }

export function PricingToggle({ interval, onToggle, savingsPct }: PricingToggleProps) {
  return (
    <div className="flex items-center justify-center gap-3">
      <span className={`text-sm ${interval === "monthly" ? "font-semibold" : "text-gray-500"}`}>Monthly</span>
      <button onClick={() => onToggle(interval === "monthly" ? "yearly" : "monthly")}
        className="relative h-6 w-11 rounded-full bg-gray-300 transition dark:bg-gray-600" role="switch" aria-checked={interval === "yearly"}>
        <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${interval === "yearly" ? "translate-x-5" : "translate-x-0.5"}`} />
      </button>
      <span className={`text-sm ${interval === "yearly" ? "font-semibold" : "text-gray-500"}`}>
        Yearly {savingsPct ? <span className="text-green-600 text-xs">Save {savingsPct}%</span> : null}
      </span>
    </div>
  );
}
