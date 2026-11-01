import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CdnStatsCard } from "@/components/cdn-stats-card";

describe("CdnStatsCard", () => {
  it("renders CDN stats", () => {
    const onPurge = vi.fn();
    const { container, getByText } = render(
      <CdnStatsCard domain="cdn.example.com" hitRate={80} hitRateDisplay="80.0%"
        hits={800} misses={200} cachedPaths={50} purges={3} health="good" onPurge={onPurge} />
    );
    expect(container.textContent).toContain("CDN Cache");
    expect(container.textContent).toContain("cdn.example.com");
    expect(container.textContent).toContain("80.0%");
    expect(container.textContent).toContain("good");
    expect(container.textContent).toContain("800");
    fireEvent.click(getByText("Purge All"));
    expect(onPurge).toHaveBeenCalled();
  });
});
