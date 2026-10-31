import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RespCacheStats } from "@/components/resp-cache-stats";

describe("RespCacheStats", () => {
  it("renders stats", () => {
    const { container } = render(
      <RespCacheStats totalKeys={100} active={90} totalHits={5000} onClear={vi.fn()} />
    );
    expect(container.textContent).toContain("Response Cache");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("90");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("Flush");
  });
});
