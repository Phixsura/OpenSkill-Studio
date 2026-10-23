"use client";

import { useState } from "react";

interface NpsSurveyWidgetProps { appName: string; onSubmit: (score: number, feedback: string) => void; }

export function NpsSurveyWidget({ appName, onSubmit }: NpsSurveyWidgetProps) {
  const [score, setScore] = useState<number | null>(null);
  const [feedback, setFeedback] = useState("");

  return (
    <div className="rounded-lg border p-5 dark:border-gray-700">
      <h3 className="text-center font-semibold">How likely are you to recommend {appName}?</h3>
      <div className="mt-4 flex justify-center gap-1">
        {Array.from({ length: 11 }, (_, i) => (
          <button key={i} onClick={() => setScore(i)}
            className={`h-9 w-9 rounded text-sm font-bold ${score === i ? (i >= 9 ? "bg-green-600 text-white" : i >= 7 ? "bg-yellow-500 text-white" : "bg-red-500 text-white") : "border dark:border-gray-600"}`}>
            {i}
          </button>
        ))}
      </div>
      <div className="mt-1 flex justify-between text-xs text-gray-400">
        <span>Not at all likely</span><span>Extremely likely</span>
      </div>
      {score !== null && (
        <>
          <textarea value={feedback} onChange={e => setFeedback(e.target.value)}
            placeholder="Tell us more (optional)..." rows={2}
            className="mt-3 w-full rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
          <button onClick={() => onSubmit(score, feedback)}
            className="mt-2 w-full rounded bg-blue-600 py-2 text-sm font-medium text-white">
            Submit
          </button>
        </>
      )}
    </div>
  );
}
