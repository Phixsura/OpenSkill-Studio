"use client";
export function FleetAiContainerPanel({ runtimes, active, containers, images, startup }: { runtimes: number; active: number; containers: number; images: number; startup: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐳 AI Containers</h3>
    <div className="text-sm">{active}/{runtimes} active · {containers} containers · {images} images · {startup}s startup</div>
  </div>);
}
