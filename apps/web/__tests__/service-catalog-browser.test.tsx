import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ServiceCatalogBrowser } from "@/components/service-catalog-browser";

describe("ServiceCatalogBrowser", () => {
  it("renders catalog", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <ServiceCatalogBrowser byTeam={{ platform: 2 }} onSelect={onSelect}
        services={[
          { id: "auth", name: "Auth Service", team: "platform", tier: "tier0", description: "Authentication", dependencies: [] },
          { id: "billing", name: "Billing", team: "commerce", tier: "tier1", description: "Payment processing", dependencies: ["auth"] },
        ]} />
    );
    expect(container.textContent).toContain("Service Catalog");
    expect(container.textContent).toContain("2 services");
    expect(container.textContent).toContain("Auth Service");
    expect(container.textContent).toContain("tier0");
    expect(container.textContent).toContain("Billing");
    fireEvent.click(getByText("Billing"));
    expect(onSelect).toHaveBeenCalledWith("billing");
  });
});
