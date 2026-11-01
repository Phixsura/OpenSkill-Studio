import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CacheManagerPanel } from "@/components/cache-manager-panel";

const mockStats = { hits: 800, misses: 200, hitRate: 80, l1Size: 100, l2Size: 500, l1Hits: 600, l2Hits: 200 };

describe("CacheManagerPanel", () => {
  it("renders cache stats", () => {
    const { container } = render(<CacheManagerPanel stats={mockStats} />);
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("600 hits");
    expect(container.textContent).toContain("200 hits");
  });

  it("calls onClear", () => {
    const onClear = vi.fn();
    const { getByText } = render(<CacheManagerPanel stats={mockStats} onClear={onClear} />);
    fireEvent.click(getByText("Clear All"));
    expect(onClear).toHaveBeenCalled();
  });
});
