"use client";

import { useState } from "react";

interface Question { id: string; text: string; type: string; required: boolean; options: string[] | null; }
interface FeedbackSurveyProps { title: string; questions: Question[];
  onSubmit: (answers: Record<string, string | number>) => void; }

export function FeedbackSurvey({ title, questions, onSubmit }: FeedbackSurveyProps) {
  const [answers, setAnswers] = useState<Record<string, string | number>>({});
  const update = (id: string, value: string | number) => setAnswers(prev => ({ ...prev, [id]: value }));

  return (
    <div className="mx-auto max-w-md space-y-4">
      <h2 className="text-lg font-bold">{title}</h2>
      {questions.map(q => (
        <div key={q.id}>
          <label className="block text-sm font-medium mb-1">{q.text}{q.required && <span className="text-red-500"> *</span>}</label>
          {q.type === "rating" && (
            <div className="flex gap-1">{[1, 2, 3, 4, 5].map(n => (
              <button key={n} onClick={() => update(q.id, n)}
                className={`h-9 w-9 rounded-lg text-sm ${answers[q.id] === n ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{n}</button>
            ))}</div>
          )}
          {q.type === "text" && (
            <textarea onChange={e => update(q.id, e.target.value)} rows={2}
              className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
          )}
          {q.type === "nps" && (
            <div className="flex gap-0.5">{Array.from({ length: 11 }, (_, i) => (
              <button key={i} onClick={() => update(q.id, i)}
                className={`h-8 w-8 rounded text-xs ${answers[q.id] === i ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{i}</button>
            ))}</div>
          )}
        </div>
      ))}
      <button onClick={() => onSubmit(answers)} className="w-full rounded bg-blue-600 py-2 text-sm text-white">Submit</button>
    </div>
  );
}
