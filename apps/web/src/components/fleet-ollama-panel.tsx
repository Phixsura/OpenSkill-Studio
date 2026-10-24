"use client";
export function FleetOllamaPanel({ instances, running, modelsLoaded, requests }: { instances: number; running: number; modelsLoaded: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🦙 Ollama</h3>
    <div className="text-sm">{running}/{instances} running · {modelsLoaded} models · {requests.toLocaleString()} req</div>
  </div>);
}
