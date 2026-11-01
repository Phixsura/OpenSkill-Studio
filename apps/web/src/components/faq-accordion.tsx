"use client";
import { useState } from "react";

interface FaqItem { id: string; question: string; answer: string; category: string; }
interface FaqAccordionProps { items: FaqItem[]; }

export function FaqAccordion({ items }: FaqAccordionProps) {
  const [open, setOpen] = useState<string | null>(null);
  return (
    <div className="rounded-xl border dark:border-gray-700 divide-y dark:divide-gray-700">
      {items.map(f => (
        <div key={f.id}>
          <button onClick={() => setOpen(open === f.id ? null : f.id)}
            className="w-full text-left px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800">
            <span className="text-sm font-medium">{f.question}</span>
            <span className="text-xs text-gray-400">{open === f.id ? "−" : "+"}</span>
          </button>
          {open === f.id && (
            <div className="px-4 pb-3 text-sm text-gray-500">{f.answer}</div>
          )}
        </div>
      ))}
    </div>
  );
}
