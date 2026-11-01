import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChaosInjectPanel } from "@/components/chaos-inject-panel";

describe("ChaosInjectPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ChaosInjectPanel activeCount={2}
        experiments={[
          { type: "latency", service: "api", active: true, addedMs: 300 },
          { type: "error", service: "db", triggered: true },
          { type: "network_partition", active: false },
        ]} />
    );
    expect(container.textContent).toContain("Chaos Engineering");
    expect(container.textContent).toContain("2 active / 3 total");
    expect(container.textContent).toContain("latency");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("ACTIVE");
  });
});
