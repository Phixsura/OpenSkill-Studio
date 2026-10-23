import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcCatalogBrowser } from "@/components/svc-catalog-browser";

describe("SvcCatalogBrowser", () => {
  it("renders catalog", () => {
    const { container } = render(
      <SvcCatalogBrowser total={3} healthy={2} byTier={{ critical: 2, standard: 1 }}
        services={[
          { name: "auth-service", description: "Auth", tier: "critical", owner: "platform", status: "healthy" },
          { name: "email-worker", description: "Email", tier: "standard", owner: "platform", status: "degraded" },
        ]} />
    );
    expect(container.textContent).toContain("Service Catalog");
    expect(container.textContent).toContain("3 services");
    expect(container.textContent).toContain("2 healthy");
    expect(container.textContent).toContain("auth-service");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("email-worker");
  });
});
