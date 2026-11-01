"use client";
export function FleetAiTokenizerPanel({ tokenizers, active, vocabSize, tokens, compression }: { tokenizers: number; active: number; vocabSize: number; tokens: number; compression: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✂️ AI Tokenizer</h3>
    <div className="text-sm">{active}/{tokenizers} active · {vocabSize.toLocaleString()} vocab · {tokens.toLocaleString()} tok · {compression}x compress</div>
  </div>);
}
