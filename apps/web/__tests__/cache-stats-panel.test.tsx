import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CacheStatsPanel } from "@/components/cache-stats-panel";

const mockStats = {
  entries: 750, sizeBytes: 25 * 1024 * 1024, hits: 15000, misses: 3000,
  hitRate: 83.3, maxEntries: 1000, maxSizeBytes: 50 * 1024 * 1024,
};

describe("CacheStatsPanel", () => {
  it("renders cache metrics", () => {
    const { container } = render(<CacheStatsPanel stats={mockStats} />);
    expect(container.textContent).toContain("83.3%");
    expect(container.textContent).toContain("15,000");
    expect(container.textContent).toContain("3,000");
    expect(container.textContent).toContain("750");
  });

  it("shows size bars", () => {
    const { container } = render(<CacheStatsPanel stats={mockStats} />);
    expect(container.textContent).toContain("750/1000");
    expect(container.textContent).toContain("25.0MB");
  });

  it("calls onClear", () => {
    const onClear = vi.fn();
    const { getByText } = render(<CacheStatsPanel stats={mockStats} onClear={onClear} />);
    fireEvent.click(getByText("Clear All"));
    expect(onClear).toHaveBeenCalled();
  });
});
