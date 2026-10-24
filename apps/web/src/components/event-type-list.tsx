"use client";

interface EventType { name: string; category: string; description: string; }

interface EventTypeListProps {
  events: EventType[];
  selectedCategory?: string;
  onSelect?: (eventType: string) => void;
}

const CATEGORY_COLORS: Record<string, string> = {
  submission: "blue", cohort: "purple", project: "green", app: "cyan",
  pack: "orange", workflow: "indigo", talent: "pink", evaluation: "yellow",
};

export function EventTypeList({ events, selectedCategory, onSelect }: EventTypeListProps) {
  const filtered = selectedCategory ? events.filter(e => e.category === selectedCategory) : events;

  if (filtered.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No events</p>;

  return (
    <ul className="space-y-1">
      {filtered.map(e => (
        <li key={e.name}
          onClick={() => onSelect?.(e.name)}
          className={`flex items-center justify-between rounded border border-gray-200 p-2 text-sm dark:border-gray-700 ${onSelect ? "cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800" : ""}`}>
          <div>
            <span className="font-mono text-xs font-medium">{e.name}</span>
            <p className="text-xs text-gray-500">{e.description}</p>
          </div>
          <span className={`rounded-full bg-${CATEGORY_COLORS[e.category] ?? "gray"}-100 px-2 py-0.5 text-xs dark:bg-${CATEGORY_COLORS[e.category] ?? "gray"}-900`}>
            {e.category}
          </span>
        </li>
      ))}
    </ul>
  );
}
