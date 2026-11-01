import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CacheStats } from "@/components/cache-stats";

describe("CacheStats", () => {
  it("renders stats", () => {
    const { container } = render(
      <CacheStats size={50} maxSize={100} hits={200} misses={50} hitRate={80} ttlS={300} onClear={vi.fn()} />
    );
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("50/100");
    expect(container.textContent).toContain("300s");
    expect(container.textContent).toContain("200 hits");
    expect(container.textContent).toContain("50 misses");
  });
  it("clear", () => {
    const fn = vi.fn();
    const { container } = render(
      <CacheStats size={10} maxSize={100} hits={0} misses={0} hitRate={0} ttlS={60} onClear={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
