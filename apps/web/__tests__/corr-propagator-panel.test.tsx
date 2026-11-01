import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CorrPropagatorPanel } from "@/components/corr-propagator-panel";
describe("CorrPropagatorPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CorrPropagatorPanel correlationId="corr-abc123" headerName="X-Correlation-ID"
        chain={["gateway", "api", "db"]} />
    );
    expect(container.textContent).toContain("Correlation Propagator");
    expect(container.textContent).toContain("X-Correlation-ID");
    expect(container.textContent).toContain("3 hops");
    expect(container.textContent).toContain("corr-abc123");
    expect(container.textContent).toContain("gateway");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
  });
});
