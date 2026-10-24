import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DedupCachePanel } from "@/components/dedup-cache-panel";
describe("DedupCachePanel", () => {
  it("renders", () => {
    const { container } = render(
      <DedupCachePanel size={5000} hits={8000} misses={2000} hitRate={80} maxSize={10000} />
    );
    expect(container.textContent).toContain("Dedup Cache");
    expect(container.textContent).toContain("80% hit rate");
    expect(container.textContent).toContain("5,000/10,000");
    expect(container.textContent).toContain("8,000");
    expect(container.textContent).toContain("2,000");
  });
});
