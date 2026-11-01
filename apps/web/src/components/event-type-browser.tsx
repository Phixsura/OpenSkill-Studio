"use client";

interface EventType { type: string; description: string; category: string; }
interface EventTypeBrowserProps { groups: string[]; events: EventType[];
  selectedGroup: string | null; onSelectGroup: (g: string | null) => void; }

export function EventTypeBrowser({ groups, events, selectedGroup, onSelectGroup }: EventTypeBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold mb-2">📡 Event Types</h3>
        <div className="flex gap-1">
          <button onClick={() => onSelectGroup(null)}
            className={`text-xs px-2 py-1 rounded ${!selectedGroup ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
          {groups.map(g => (
            <button key={g} onClick={() => onSelectGroup(g)}
              className={`text-xs px-2 py-1 rounded capitalize ${selectedGroup === g ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{g}</button>
          ))}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-64 overflow-y-auto">
        {events.map(e => (
          <div key={e.type} className="px-4 py-2 flex items-center justify-between">
            <div>
              <code className="text-xs font-bold text-blue-600">{e.type}</code>
              <p className="text-xs text-gray-500">{e.description}</p>
            </div>
            <span className="text-xs text-gray-400 capitalize">{e.category}</span>
          </div>
        ))}
      </div>
      <div className="px-4 py-2 text-xs text-gray-400 border-t dark:border-gray-700">{events.length} event types</div>
    </div>
  );
}
