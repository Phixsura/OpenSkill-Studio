import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EndpointCoveragePanel } from "@/components/endpoint-coverage-panel";

describe("EndpointCoveragePanel", () => {
  it("renders", () => {
    const { container } = render(
      <EndpointCoveragePanel coveragePct={75} covered={3} total={4}
        uncoveredPaths={["/orders"]}
        byMethod={{ GET: { total: 3, covered: 2 }, POST: { total: 1, covered: 1 } }} />
    );
    expect(container.textContent).toContain("Endpoint Coverage");
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("3/4");
    expect(container.textContent).toContain("GET: 2/3");
    expect(container.textContent).toContain("/orders");
  });
});
