import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CachePolicyPanel } from "@/components/cache-policy-panel";
describe("CachePolicyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CachePolicyPanel cacheableCount={1}
        policies={[
          { endpoint: "/api/users", ttl: 300, cacheable: true, varyBy: ["Authorization"] },
          { endpoint: "/api/auth", ttl: 0, cacheable: false, varyBy: [] },
        ]} />
    );
    expect(container.textContent).toContain("Cache Policies");
    expect(container.textContent).toContain("1/2 cacheable");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("300s");
    expect(container.textContent).toContain("vary: Authorization");
    expect(container.textContent).toContain("no-store");
  });
});
