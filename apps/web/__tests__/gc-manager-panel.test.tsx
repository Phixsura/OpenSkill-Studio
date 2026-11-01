import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GcManagerPanel } from "@/components/gc-manager-panel";
describe("GcManagerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GcManagerPanel stale={1} orphaned={1} reclaimableMb={80}
        items={[
          { id: "tmp-1", type: "temp", sizeMb: 50 },
          { id: "orphan-1", type: "volume", sizeMb: 30 },
        ]} />
    );
    expect(container.textContent).toContain("Garbage Collector");
    expect(container.textContent).toContain("1 stale");
    expect(container.textContent).toContain("1 orphaned");
    expect(container.textContent).toContain("80MB reclaimable");
    expect(container.textContent).toContain("tmp-1");
  });
});
