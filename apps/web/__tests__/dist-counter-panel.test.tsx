import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DistCounterPanel } from "@/components/dist-counter-panel";
describe("DistCounterPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DistCounterPanel total={60} shards={4} shardValues={[5, 20, 30, 5]} />
    );
    expect(container.textContent).toContain("Distributed Counter");
    expect(container.textContent).toContain("4 shards");
    expect(container.textContent).toContain("total: 60");
    expect(container.textContent).toContain("shard-0");
    expect(container.textContent).toContain("20");
  });
});
