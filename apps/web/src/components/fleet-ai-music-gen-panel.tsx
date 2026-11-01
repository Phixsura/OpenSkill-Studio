"use client";
export function FleetAiMusicGenPanel({ generators, active, tracks, genres, duration }: { generators: number; active: number; tracks: number; genres: number; duration: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎵 AI Music Generation</h3>
    <div className="text-sm">{active}/{generators} active · {tracks.toLocaleString()} tracks · {genres} genres · {duration}s avg</div>
  </div>);
}
