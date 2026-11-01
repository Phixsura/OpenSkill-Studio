"use client";

interface Plan { id: string; name: string; priceDisplay: string; recommended: boolean; }
interface CellValue { display: string; type: string; value: unknown; }
interface Feature { name: string; values: Record<string, CellValue>; }
interface PricingComparisonTableProps { plans: Plan[]; features: Feature[]; onSelect: (id: string) => void; }

export function PricingComparisonTable({ plans, features, onSelect }: PricingComparisonTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead><tr className="border-b dark:border-gray-700">
          <th className="px-4 py-3 text-left font-medium w-48">Feature</th>
          {plans.map(p => (
            <th key={p.id} className="px-4 py-3 text-center">
              {p.recommended && <span className="mb-1 block text-xs text-blue-600">★ Recommended</span>}
              <span className="font-bold">{p.name}</span>
              <p className="text-xs text-gray-400 font-normal">{p.priceDisplay}</p>
            </th>
          ))}
        </tr></thead>
        <tbody>{features.map(f => (
          <tr key={f.name} className="border-b dark:border-gray-800">
            <td className="px-4 py-2.5 font-medium">{f.name}</td>
            {plans.map(p => {
              const cell = f.values[p.id];
              return <td key={p.id} className={`px-4 py-2.5 text-center ${cell?.type === "bool" ? (cell.value ? "text-green-600" : "text-gray-300") : ""}`}>{cell?.display}</td>;
            })}
          </tr>
        ))}</tbody>
        <tfoot><tr>
          <td></td>
          {plans.map(p => (
            <td key={p.id} className="px-4 py-3 text-center">
              <button onClick={() => onSelect(p.id)}
                className={`rounded-lg px-4 py-2 text-sm ${p.recommended ? "bg-blue-600 text-white" : "border dark:border-gray-700"}`}>
                {p.priceDisplay === "Free" ? "Get Started" : p.priceDisplay === "Custom" ? "Contact Sales" : "Subscribe"}
              </button>
            </td>
          ))}
        </tr></tfoot>
      </table>
    </div>
  );
}
