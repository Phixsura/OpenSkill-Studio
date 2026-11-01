"use client";

import { useState } from "react";

interface ResourceLimitsEditorProps {
  memoryMb: number;
  timeoutSeconds: number;
  maxMemory?: number;
  maxTimeout?: number;
  onChange: (limits: { memoryMb: number; timeoutSeconds: number }) => void;
}

export function ResourceLimitsEditor({ memoryMb, timeoutSeconds, maxMemory = 512, maxTimeout = 120, onChange }: ResourceLimitsEditorProps) {
  const [mem, setMem] = useState(memoryMb);
  const [timeout, setTimeout_] = useState(timeoutSeconds);

  const handleChange = (newMem: number, newTimeout: number) => {
    setMem(newMem);
    setTimeout_(newTimeout);
    onChange({ memoryMb: newMem, timeoutSeconds: newTimeout });
  };

  return (
    <div className="space-y-3">
      <div>
        <label className="text-sm font-medium">Memory: {mem} MB</label>
        <input type="range" min={32} max={maxMemory} step={32} value={mem}
          onChange={e => handleChange(Number(e.target.value), timeout)}
          className="w-full" />
        <div className="flex justify-between text-xs text-gray-400"><span>32 MB</span><span>{maxMemory} MB</span></div>
      </div>
      <div>
        <label className="text-sm font-medium">Timeout: {timeout}s</label>
        <input type="range" min={5} max={maxTimeout} step={5} value={timeout}
          onChange={e => handleChange(mem, Number(e.target.value))}
          className="w-full" />
        <div className="flex justify-between text-xs text-gray-400"><span>5s</span><span>{maxTimeout}s</span></div>
      </div>
    </div>
  );
}
