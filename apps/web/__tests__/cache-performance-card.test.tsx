import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CachePerformanceCard } from "@/components/cache-performance-card";

describe("CachePerformanceCard", () => {
  it("renders stats", () => {
    const { container } = render(
      <CachePerformanceCard hits={9000} misses={1000} hitRate={90} efficiency="good" onPurge={vi.fn()} />
    );
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("9,000");
    expect(container.textContent).toContain("good");
  });
  it("purge button", () => {
    const fn = vi.fn();
    const { container } = render(
      <CachePerformanceCard hits={0} misses={0} hitRate={0} efficiency="poor" onPurge={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Purge")!);
    expect(fn).toHaveBeenCalled();
  });
});
