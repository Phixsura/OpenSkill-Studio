import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwObservPanel } from "@/components/gw-observ-panel";
describe("GwObservPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GwObservPanel total={10000} avgMs={45} errorRatePct={0.5}
        byStatus={{ "2xx": 9500, "4xx": 450, "5xx": 50 }}
        topRoutes={[{ route: "/api/users", count: 5000 }, { route: "/api/orders", count: 3000 }]} />
    );
    expect(container.textContent).toContain("Gateway Observability");
    expect(container.textContent).toContain("10,000 reqs");
    expect(container.textContent).toContain("45ms avg");
    expect(container.textContent).toContain("5xx: 50");
    expect(container.textContent).toContain("/api/users");
  });
});
