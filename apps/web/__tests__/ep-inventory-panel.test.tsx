import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpInventoryPanel } from "@/components/ep-inventory-panel";
describe("EpInventoryPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpInventoryPanel total={4} deprecated={1} services={3}
        endpoints={[
          { method: "GET", path: "/api/v1/users", service: "user-svc", deprecated: false },
          { method: "GET", path: "/api/v0/legacy", service: "legacy-svc", deprecated: true },
        ]} />
    );
    expect(container.textContent).toContain("Endpoint Inventory");
    expect(container.textContent).toContain("4 endpoints");
    expect(container.textContent).toContain("3 services");
    expect(container.textContent).toContain("1 deprecated");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/v1/users");
  });
});
