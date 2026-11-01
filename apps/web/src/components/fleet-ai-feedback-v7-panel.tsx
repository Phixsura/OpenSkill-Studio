"use client";
export function FleetAiFeedbackV7Panel({ systems, active, feedback, positive, actioned }: { systems: number; active: number; feedback: number; positive: number; actioned: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👍 AI Feedback v7</h3>
    <div className="text-sm">{active}/{systems} active · {feedback.toLocaleString()} feedback · {positive.toLocaleString()} positive · {actioned.toLocaleString()} actioned</div>
  </div>);
}
