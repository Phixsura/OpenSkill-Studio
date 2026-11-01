"use client";
export function FleetAiIntentClsPanel({ classifiers, active, classified, intents, accuracy }: { classifiers: number; active: number; classified: number; intents: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 AI Intent Classifier</h3>
    <div className="text-sm">{active}/{classifiers} active · {classified.toLocaleString()} classified · {intents} intents · {accuracy}% acc</div>
  </div>);
}
