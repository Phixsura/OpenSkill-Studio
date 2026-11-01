"use client";

interface Panel { id: number; title: string; type: string; metric: string; width: number; }
interface DashBuilderProps { title: string; panels: Panel[]; onAddPanel: () => void; }

const TYPE_ICONS: Record<string, string> = {
  chart: "📈", gauge: "🎯", counter: "🔢", table: "📋", heatmap: "🔥",
};

export function DashBuilder({ title, panels, onAddPanel }: DashBuilderProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 {title}</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{panels.length} panels</span>
          <button onClick={onAddPanel} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Panel</button>
        </div>
      </div>
      <div className="grid grid-cols-12 gap-2 p-3">
        {panels.map(p => (
          <div key={p.id} className="border dark:border-gray-700 rounded-lg p-2 text-center"
            style={{ gridColumn: `span ${Math.min(p.width, 12)}` }}>
            <div className="text-lg">{TYPE_ICONS[p.type] ?? "📊"}</div>
            <div className="text-xs font-medium">{p.title}</div>
            <div className="text-[10px] text-gray-400">{p.metric}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
