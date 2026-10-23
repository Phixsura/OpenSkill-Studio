"use client";

interface Tab { id: string; label: string; icon: string; badge: number | null;
  active: boolean; disabled: boolean; }
interface TabBarProps { tabs: Tab[]; onSelect: (id: string) => void; }

export function TabBar({ tabs, onSelect }: TabBarProps) {
  return (
    <div className="flex border-b dark:border-gray-700">
      {tabs.map(t => (
        <button key={t.id} onClick={() => !t.disabled && onSelect(t.id)} disabled={t.disabled}
          className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
            t.active ? "border-blue-500 text-blue-600" :
            t.disabled ? "border-transparent text-gray-300 cursor-not-allowed" :
            "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
          }`}>
          {t.icon && <span>{t.icon}</span>}
          {t.label}
          {t.badge != null && t.badge > 0 && (
            <span className="text-xs px-1.5 py-0.5 rounded-full bg-red-500 text-white font-bold">{t.badge}</span>
          )}
        </button>
      ))}
    </div>
  );
}
