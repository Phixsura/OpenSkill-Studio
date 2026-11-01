"use client";
export function FleetAiTextClsPanel({ classifiers, active, classified, labels, zeroShot, f1 }: { classifiers: number; active: number; classified: number; labels: number; zeroShot: number; f1: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏷️ AI Text Classifier v2</h3>
    <div className="text-sm">{active}/{classifiers} active · {classified.toLocaleString()} classified · {labels} labels · {zeroShot}% zero-shot · F1 {f1}</div>
  </div>);
}
