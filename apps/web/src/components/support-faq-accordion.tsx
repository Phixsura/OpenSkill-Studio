"use client";

import { useState } from "react";

interface FaqItem { id: string; question: string; answer: string; category: string; }
interface SupportFaqAccordionProps { items: FaqItem[]; }

export function SupportFaqAccordion({ items }: SupportFaqAccordionProps) {
  const [openId, setOpenId] = useState<string | null>(null);

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b p-3 dark:border-gray-700">
        <h3 className="text-sm font-semibold">Frequently Asked Questions</h3>
      </div>
      {items.map(item => (
        <div key={item.id} className="border-b last:border-0 dark:border-gray-700">
          <button onClick={() => setOpenId(openId === item.id ? null : item.id)}
            className="flex w-full items-center justify-between px-4 py-3 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
            <span className="font-medium">{item.question}</span>
            <span className="text-gray-400">{openId === item.id ? "−" : "+"}</span>
          </button>
          {openId === item.id && (
            <div className="px-4 pb-3 text-sm text-gray-600 dark:text-gray-400">{item.answer}</div>
          )}
        </div>
      ))}
    </div>
  );
}
