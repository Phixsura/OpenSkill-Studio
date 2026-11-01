import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EndpointCatPanel } from "@/components/endpoint-cat-panel";
describe("EndpointCatPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EndpointCatPanel total={3} services={2}
        endpoints={[
          { method: "GET", path: "/api/users", service: "user-svc", authRequired: true, rateLimit: 100 },
          { method: "POST", path: "/api/orders", service: "order-svc", authRequired: true, rateLimit: 50 },
        ]} />
    );
    expect(container.textContent).toContain("API Catalog");
    expect(container.textContent).toContain("3 endpoints");
    expect(container.textContent).toContain("2 services");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("user-svc");
  });
});
