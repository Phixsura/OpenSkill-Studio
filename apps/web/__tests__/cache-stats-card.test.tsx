import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CacheStatsCard } from "@/components/cache-stats-card";

describe("CacheStatsCard", () => {
  it("renders and flushes", () => {
    const onFlush = vi.fn();
    const { container, getByText } = render(
      <CacheStatsCard size={500} maxSize={1000} hits={4000} misses={600}
        hitRateDisplay="87.0%" onFlush={onFlush} />
    );
    expect(container.textContent).toContain("Response Cache");
    expect(container.textContent).toContain("87.0%");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("4000");
    fireEvent.click(getByText("Flush Cache"));
    expect(onFlush).toHaveBeenCalled();
  });
});
