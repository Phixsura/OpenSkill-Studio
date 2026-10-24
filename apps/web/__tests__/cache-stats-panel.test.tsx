import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CacheStatsPanel } from "@/components/cache-stats-panel";

describe("CacheStatsPanel", () => {
  const caches = [
    { name: "L1", type: "memory", size_mb: 64, max_size_mb: 128, hits: 900, misses: 100, hit_rate: 90, evictions: 50 },
  ];
  it("renders", () => {
    const { container } = render(<CacheStatsPanel caches={caches} overallHitRate={90} onInvalidate={vi.fn()} />);
    expect(container.textContent).toContain("Cache");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("L1");
    expect(container.textContent).toContain("memory");
    expect(container.textContent).toContain("50 evictions");
  });
  it("flush", () => {
    const fn = vi.fn();
    const { container } = render(<CacheStatsPanel caches={caches} overallHitRate={90} onInvalidate={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Flush")!);
    expect(fn).toHaveBeenCalledWith("L1");
  });
});
