import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CacheStatsCard } from "@/components/cache-stats-card";

describe("CacheStatsCard", () => {
  it("renders stats", () => {
    const { container } = render(<CacheStatsCard entries={42} totalHits={1500} hitRate={85} onClear={vi.fn()} />);
    expect(container.textContent).toContain("42");
    expect(container.textContent).toContain("1,500");
    expect(container.textContent).toContain("85%");
  });
  it("calls onClear", () => {
    const fn = vi.fn();
    const { container } = render(<CacheStatsCard entries={0} totalHits={0} hitRate={0} onClear={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
