"use client";
export function FleetAiObjDetectPanel({ detectors, active, frames, objects, mapScore }: { detectors: number; active: number; frames: number; objects: number; mapScore: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 AI Object Detection</h3>
    <div className="text-sm">{active}/{detectors} active · {frames.toLocaleString()} frames · {objects.toLocaleString()} objects · mAP {mapScore}%</div>
  </div>);
}
