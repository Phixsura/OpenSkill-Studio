"use client";

import { useState } from "react";

interface MenuItem { id: string; label: string; icon: string | null; danger: boolean;
  separator_before: boolean; disabled: boolean; }
interface DropdownMenuProps { trigger: React.ReactNode; items: MenuItem[];
  onSelect: (id: string) => void; }

export function DropdownMenu({ trigger, items, onSelect }: DropdownMenuProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative inline-block">
      <div onClick={() => setOpen(!open)}>{trigger}</div>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 z-50 mt-1 w-48 rounded-lg border bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-900">
            {items.map(item => (
              <div key={item.id}>
                {item.separator_before && <div className="my-1 border-t dark:border-gray-700" />}
                <button onClick={() => { onSelect(item.id); setOpen(false); }}
                  disabled={item.disabled}
                  className={`flex w-full items-center gap-2 px-3 py-2 text-left text-sm disabled:opacity-40 ${item.danger ? "text-red-600 hover:bg-red-50 dark:hover:bg-red-900/10" : "hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
                  {item.icon && <span>{item.icon}</span>}
                  <span>{item.label}</span>
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
