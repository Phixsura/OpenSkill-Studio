"use client";
interface EventRoute { eventType: string; handlers: number; }
interface WhEventRouterPanelProps { routes: EventRoute[]; totalDelivered: number; }
export function WhEventRouterPanel({ routes, totalDelivered }: WhEventRouterPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Event Router</h3>
        <span className="text-xs text-gray-400">{routes.length} types · {totalDelivered.toLocaleString()} delivered</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {routes.map(r => (
          <div key={r.eventType} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{r.eventType}</span>
            <span className="text-gray-400">{r.handlers} handlers</span>
          </div>
        ))}
      </div>
    </div>
  );
}
