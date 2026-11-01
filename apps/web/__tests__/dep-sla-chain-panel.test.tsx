import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepSlaChainPanel } from "@/components/dep-sla-chain-panel";
describe("DepSlaChainPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepSlaChainPanel compositeSla={99.79} downtimeMinMonth={90.7} meetsTarget={false}
        chain={[
          { service: "gateway", slaPct: 99.99 },
          { service: "api", slaPct: 99.9 },
          { service: "db", slaPct: 99.9 },
        ]} />
    );
    expect(container.textContent).toContain("Dependency SLA Chain");
    expect(container.textContent).toContain("99.79% composite");
    expect(container.textContent).toContain("90.7min/mo");
    expect(container.textContent).toContain("gateway (99.99%)");
    expect(container.textContent).toContain("api (99.9%)");
    expect(container.textContent).toContain("= 99.79%");
  });
});
