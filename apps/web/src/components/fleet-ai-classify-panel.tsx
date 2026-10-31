"use client";
export function FleetAiClassifyPanel({ classifiers, active, predictions, classes, accuracy }: { classifiers: number; active: number; predictions: number; classes: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏷️ AI Classification</h3>
    <div className="text-sm">{active}/{classifiers} active · {predictions.toLocaleString()} preds · {classes} classes · {accuracy}% acc</div>
  </div>);
}
