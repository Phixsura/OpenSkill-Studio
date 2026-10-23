"use client";

import { useState } from "react";

interface InfoTooltipProps { title: string; content: string; link?: string; }

export function InfoTooltip({ title, content, link }: InfoTooltipProps) {
  const [visible, setVisible] = useState(false);
  return (
    <span className="relative inline-block">
      <button onMouseEnter={() => setVisible(true)} onMouseLeave={() => setVisible(false)}
        className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-gray-200 text-[10px] text-gray-500 dark:bg-gray-700">
        ?
      </button>
      {visible && (
        <div className="absolute bottom-6 left-1/2 z-50 w-56 -translate-x-1/2 rounded-lg border bg-white p-3 shadow-lg dark:border-gray-700 dark:bg-gray-900">
          <h4 className="text-xs font-bold">{title}</h4>
          <p className="mt-1 text-xs text-gray-500">{content}</p>
          {link && (
            <a href={link} className="mt-1 block text-xs text-blue-500 hover:underline">Learn more →</a>
          )}
        </div>
      )}
    </span>
  );
}
