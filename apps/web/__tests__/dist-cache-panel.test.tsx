import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DistCachePanel } from "@/components/dist-cache-panel";
describe("DistCachePanel", () => {
  it("renders", () => {
    const { container } = render(
      <DistCachePanel shards={4} hits={9000} misses={1000} hitRate={90}
        totalKeys={5000} shardSizes={{ "0": 1200, "1": 1300, "2": 1250, "3": 1250 }} />
    );
    expect(container.textContent).toContain("Distributed Cache");
    expect(container.textContent).toContain("90% hit");
    expect(container.textContent).toContain("5,000 keys");
    expect(container.textContent).toContain("9,000");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("shard-0");
  });
});
