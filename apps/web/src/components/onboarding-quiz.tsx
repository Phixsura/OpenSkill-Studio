"use client";

import { useState } from "react";

interface Question { id: string; text: string; options: string[]; }
interface OnboardingQuizProps { questions: Question[]; onComplete: (answers: Record<string, string>) => void; }

export function OnboardingQuiz({ questions, onComplete }: OnboardingQuizProps) {
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const q = questions[current];
  const isLast = current === questions.length - 1;

  const handleSelect = (option: string) => {
    const newAnswers = { ...answers, [q.id]: option };
    setAnswers(newAnswers);
    if (isLast) {
      onComplete(newAnswers);
    } else {
      setCurrent(current + 1);
    }
  };

  return (
    <div className="mx-auto max-w-md rounded-lg border border-gray-200 p-6 dark:border-gray-700">
      <div className="mb-4 flex justify-between text-xs text-gray-400">
        <span>Question {current + 1} of {questions.length}</span>
      </div>
      <div className="mb-2 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${((current + 1) / questions.length) * 100}%` }} />
      </div>
      <h3 className="mt-4 text-lg font-semibold">{q?.text}</h3>
      <div className="mt-4 space-y-2">
        {q?.options.map(opt => (
          <button key={opt} onClick={() => handleSelect(opt)}
            className="w-full rounded-lg border border-gray-200 px-4 py-3 text-left text-sm hover:bg-blue-50 hover:border-blue-300 dark:border-gray-700 dark:hover:bg-blue-900/20">
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
}
