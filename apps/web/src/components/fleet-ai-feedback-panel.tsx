"use client";
export function FleetAiFeedbackPanel({ systems, active, feedback, thumbsUp, thumbsDown, satisfaction }: { systems: number; active: number; feedback: number; thumbsUp: number; thumbsDown: number; satisfaction: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👍 AI Feedback Loop</h3>
    <div className="text-sm">{active}/{systems} active · {feedback.toLocaleString()} feedback · 👍 {thumbsUp.toLocaleString()} · 👎 {thumbsDown.toLocaleString()} · {satisfaction}%</div>
  </div>);
}
