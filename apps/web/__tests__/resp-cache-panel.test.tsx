import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RespCachePanel } from "@/components/resp-cache-panel";

describe("RespCachePanel", () => {
  it("renders", () => {
    const { container } = render(
      <RespCachePanel entries={500} hits={9000} misses={1000} hitRate={90} />
    );
    expect(container.textContent).toContain("Response Cache");
    expect(container.textContent).toContain("90% hit rate");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("9,000");
    expect(container.textContent).toContain("1,000");
  });
});
