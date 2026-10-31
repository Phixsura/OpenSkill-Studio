"use client";
import { useState } from "react";

interface InfoTooltipProps { title: string; body: string; position?: string; children: React.ReactNode; }

export function InfoTooltip({ title, body, position = "top", children }: InfoTooltipProps) {
  const [visible, setVisible] = useState(false);
  const posClass = position === "bottom" ? "top-full mt-2" : position === "left" ? "right-full mr-2" :
                   position === "right" ? "left-full ml-2" : "bottom-full mb-2";
  return (
    <span className="relative inline-block" onMouseEnter={() => setVisible(true)} onMouseLeave={() => setVisible(false)}>
      {children}
      {visible && (
        <div className={`absolute z-50 ${posClass} w-48 p-2.5 bg-gray-900 text-white rounded-lg shadow-xl text-xs`}>
          <p className="font-bold mb-0.5">{title}</p>
          <p className="text-gray-300">{body}</p>
        </div>
      )}
    </span>
  );
}
