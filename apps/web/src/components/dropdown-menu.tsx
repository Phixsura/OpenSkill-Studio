"use client";

interface MenuItem { id: string; label: string; icon: string; shortcut: string;
  disabled: boolean; danger: boolean; }
interface MenuSection { group: string; items: MenuItem[]; }
interface DropdownMenuProps { sections: MenuSection[]; onSelect: (id: string) => void; }

export function DropdownMenu({ sections, onSelect }: DropdownMenuProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 bg-white dark:bg-gray-900 shadow-xl py-1 w-56">
      {sections.map((s, si) => (
        <div key={s.group}>
          {si > 0 && <div className="border-t dark:border-gray-700 my-1" />}
          {s.items.map(item => (
            <button key={item.id} onClick={() => !item.disabled && onSelect(item.id)}
              disabled={item.disabled}
              className={`w-full flex items-center justify-between px-3 py-1.5 text-sm ${
                item.danger ? "text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20" :
                item.disabled ? "text-gray-300 cursor-not-allowed" :
                "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
              }`}>
              <span className="flex items-center gap-2">
                {item.icon && <span>{item.icon}</span>}
                {item.label}
              </span>
              {item.shortcut && <kbd className="text-xs text-gray-400">{item.shortcut}</kbd>}
            </button>
          ))}
        </div>
      ))}
    </div>
  );
}
