import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpDepMapPanel } from "@/components/ep-dep-map-panel";
describe("EpDepMapPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpDepMapPanel mostComplex="/api/orders" maxDeps={3}
        endpoints={[
          { endpoint: "/api/orders", dependencies: ["user-svc", "payment-svc", "inventory-svc"], depCount: 3 },
          { endpoint: "/api/users", dependencies: ["db"], depCount: 1 },
        ]} />
    );
    expect(container.textContent).toContain("Endpoint Deps");
    expect(container.textContent).toContain("/api/orders");
    expect(container.textContent).toContain("3 deps");
    expect(container.textContent).toContain("user-svc, payment-svc, inventory-svc");
    expect(container.textContent).toContain("/api/users");
  });
});
