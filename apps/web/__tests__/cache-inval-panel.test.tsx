import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CacheInvalPanel } from "@/components/cache-inval-panel";

describe("CacheInvalPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CacheInvalPanel totalEntries={5} uniqueTags={3}
        entries={[
          { key: "user:1", tags: ["users"], ttl: 300 },
          { key: "order:1", tags: ["orders", "billing"], ttl: 60 },
        ]} />
    );
    expect(container.textContent).toContain("Cache Invalidation");
    expect(container.textContent).toContain("5 entries");
    expect(container.textContent).toContain("3 tags");
    expect(container.textContent).toContain("user:1");
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("orders");
    expect(container.textContent).toContain("300s");
  });
});
