"use client";
export function FleetContainerRegistryV9Panel({ images, vulns }: { images: number; vulns: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Container Registry v9</h3>
    <div className="text-sm">{images} images · {vulns} vulnerabilities</div>
  </div>);
}
