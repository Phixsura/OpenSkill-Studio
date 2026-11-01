"use client";

interface TextStatsProps { words: number; characters: number; sentences: number; readingTimeMin: number; }

export function TextStats({ words, characters, sentences, readingTimeMin }: TextStatsProps) {
  return (
    <div className="flex items-center gap-4 text-xs text-gray-400">
      <span>{words} words</span>
      <span>{characters} chars</span>
      <span>{sentences} sentences</span>
      <span>~{readingTimeMin} min read</span>
    </div>
  );
}
