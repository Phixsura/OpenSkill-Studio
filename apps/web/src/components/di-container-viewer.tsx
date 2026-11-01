"use client";

interface ServiceEntry { name: string; singleton: boolean; instantiated: boolean; }
interface DiContainerViewerProps { services: ServiceEntry[]; registered: number; singletonsCreated: number; }

export function DiContainerViewer({ services, registered, singletonsCreated }: DiContainerViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 DI Container</h3>
        <span className="text-xs text-gray-400">{registered} registered · {singletonsCreated} singletons</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.name}</span>
            <div className="flex items-center gap-2">
              <span className={`px-1 rounded text-[10px] ${s.singleton ? "bg-purple-100 text-purple-700" : "bg-gray-100 text-gray-700"}`}>
                {s.singleton ? "singleton" : "transient"}
              </span>
              {s.instantiated && <span className="text-green-600">●</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
