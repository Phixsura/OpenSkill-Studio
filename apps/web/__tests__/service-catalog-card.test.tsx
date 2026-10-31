import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ServiceCatalogCard from "../src/components/service-catalog-card";

const services = [
  {
    service_id: "auth",
    name: "Auth Service",
    owner: "platform-team",
    category: "core",
    health: "healthy" as const,
  },
  {
    service_id: "billing",
    name: "Billing",
    owner: "finance-team",
    category: "finance",
    health: "down" as const,
  },
];

describe("ServiceCatalogCard", () => {
  it("renders header", () => {
    const { container } = render(<ServiceCatalogCard services={services} appName="My App" />);
    expect(container.textContent).toContain("Service Catalog");
  });

  it("shows service and down counts", () => {
    const { container } = render(<ServiceCatalogCard services={services} appName="App" />);
    expect(container.textContent).toContain("2 services");
    expect(container.textContent).toContain("1 down");
  });

  it("renders service names and owners", () => {
    const { container } = render(<ServiceCatalogCard services={services} appName="App" />);
    expect(container.textContent).toContain("Auth Service");
    expect(container.textContent).toContain("platform-team");
    expect(container.textContent).toContain("core");
  });

  it("shows empty state", () => {
    const { container } = render(<ServiceCatalogCard services={[]} appName="App" />);
    expect(container.textContent).toContain("No services cataloged");
  });
});
