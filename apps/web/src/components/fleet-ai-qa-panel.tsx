"use client";
export function FleetAiQaPanel({ systems, active, questions, accuracy, sources }: { systems: number; active: number; questions: number; accuracy: number; sources: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">❓ AI Question Answerer</h3>
    <div className="text-sm">{active}/{systems} active · {questions.toLocaleString()} questions · {accuracy}% acc · {sources.toLocaleString()} sources</div>
  </div>);
}
