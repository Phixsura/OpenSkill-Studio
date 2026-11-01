"use client";

import { useState } from "react";

interface AccordionItem { index: number; title: string; content: string; icon: string | null; open: boolean; }
interface AccordionProps { items: AccordionItem[]; allowMultiple: boolean; }

export function Accordion({ items, allowMultiple }: AccordionProps) {
  const [openItems, setOpenItems] = useState<Set<number>>(new Set(items.filter(i => i.open).map(i => i.index)));

  const toggle = (index: number) => {
    setOpenItems(prev => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        if (!allowMultiple) next.clear();
        next.add(index);
      }
      return next;
    });
  };

  return (
    <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
      {items.map(item => (
        <div key={item.index}>
          <button onClick={() => toggle(item.index)}
            className="flex w-full items-center justify-between px-4 py-3 text-left">
            <div className="flex items-center gap-2">
              {item.icon && <span>{item.icon}</span>}
              <span className="text-sm font-medium">{item.title}</span>
            </div>
            <span className="text-xs text-gray-400">{openItems.has(item.index) ? "▲" : "▼"}</span>
          </button>
          {openItems.has(item.index) && (
            <div className="px-4 pb-3 text-sm text-gray-500">{item.content}</div>
          )}
        </div>
      ))}
    </div>
  );
}
