"use client";

import { useState } from "react";

interface Question { id: string; text: string; type: string; options?: string[]; max?: number; }
interface FeedbackSurveyFormProps { title: string; questions: Question[]; onSubmit: (answers: Record<string, string>) => void; onSkip: () => void; }

export function FeedbackSurveyForm({ title, questions, onSubmit, onSkip }: FeedbackSurveyFormProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const update = (id: string, value: string) => setAnswers({ ...answers, [id]: value });

  return (
    <div className="mx-auto max-w-md rounded-lg border border-gray-200 p-6 shadow-lg dark:border-gray-700">
      <h2 className="text-lg font-semibold">{title}</h2>
      <div className="mt-4 space-y-4">
        {questions.map(q => (
          <div key={q.id}>
            <label className="block text-sm font-medium">{q.text}</label>
            {q.type === "select" && q.options && (
              <select value={answers[q.id] || ""} onChange={e => update(q.id, e.target.value)}
                className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700">
                <option value="">Select...</option>
                {q.options.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            )}
            {q.type === "text" && (
              <textarea value={answers[q.id] || ""} onChange={e => update(q.id, e.target.value)} rows={2}
                className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
            )}
            {q.type === "rating" && (
              <div className="mt-1 flex gap-1">
                {Array.from({ length: q.max || 5 }, (_, i) => (
                  <button key={i} onClick={() => update(q.id, String(i + 1))}
                    className={`h-8 w-8 rounded ${answers[q.id] === String(i + 1) ? "bg-yellow-400 text-white" : "bg-gray-100 dark:bg-gray-700"}`}>
                    {i + 1}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="mt-4 flex justify-between">
        <button onClick={onSkip} className="text-sm text-gray-400">Skip</button>
        <button onClick={() => onSubmit(answers)} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Submit</button>
      </div>
    </div>
  );
}
