"use client";
export function FleetAiPlatContV2Panel({ runtimes, active, containers, images, registries }: { runtimes: number; active: number; containers: number; images: number; registries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐳 AI Container v2</h3>
    <div className="text-sm">{active}/{runtimes} active · {containers.toLocaleString()} containers · {images} images · {registries} registries</div>
  </div>);
}
