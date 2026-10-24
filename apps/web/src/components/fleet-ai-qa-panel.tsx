"use client";
export function FleetAiQaPanel({ services, active, questions, accuracy }: { services: number; active: number; questions: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">❓ AI QA</h3>
    <div className="text-sm">{active}/{services} active · {questions.toLocaleString()} questions · {accuracy}% accuracy</div>
  </div>);
}
