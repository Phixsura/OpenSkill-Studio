import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BuildCacheStats } from "@/components/build-cache-stats";

describe("BuildCacheStats", () => {
  it("renders stats", () => {
    const { container } = render(
      <BuildCacheStats totalEntries={25} totalHits={500} totalSizeMb={2500} avgHits={20} onClear={vi.fn()} />
    );
    expect(container.textContent).toContain("Build Cache");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("2500 MB");
    expect(container.textContent).toContain("20");
    expect(container.textContent).toContain("Clear");
  });
});
