import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CacheStatsCard } from "@/components/cache-stats-card";

describe("CacheStatsCard", () => {
  it("renders stats", () => {
    const { container } = render(
      <CacheStatsCard totalKeys={150} active={120} expired={30} totalHits={5000} onClear={vi.fn()} />
    );
    expect(container.textContent).toContain("Cache Stats");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("120");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("Clear All");
  });
});
