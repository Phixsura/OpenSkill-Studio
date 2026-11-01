"use client";

interface Component { name: string; type: string; estimatedCost: number; }
interface SvcBlueprintViewerProps { name: string; components: Component[];
  estimatedMonthlyCost: number; issues: string[]; valid: boolean; }

const TYPE_ICONS: Record<string, string> = {
  service: "⚙️", database: "💾", cache: "💨", queue: "📬", gateway: "🌐",
};

export function SvcBlueprintViewer({ name, components, estimatedMonthlyCost, issues, valid }: SvcBlueprintViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📐 Blueprint: {name}</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">${estimatedMonthlyCost}/mo</span>
          <span className={valid ? "text-green-600" : "text-yellow-600"}>
            {valid ? "✅ Valid" : `⚠ ${issues.length} issues`}
          </span>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2 p-3">
        {components.map(c => (
          <div key={c.name} className="border dark:border-gray-700 rounded-lg p-2 text-center text-xs">
            <div>{TYPE_ICONS[c.type] ?? "📦"}</div>
            <div className="font-mono font-bold">{c.name}</div>
            <div className="text-[10px] text-gray-400">${c.estimatedCost}/mo</div>
          </div>
        ))}
      </div>
      {issues.length > 0 && (
        <div className="p-3 border-t dark:border-gray-700 bg-yellow-50 dark:bg-yellow-900/10">
          {issues.map((i, idx) => <div key={idx} className="text-xs text-yellow-700">💡 {i}</div>)}
        </div>
      )}
    </div>
  );
}
