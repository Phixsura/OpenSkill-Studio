import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ServiceDiscoveryPanel } from "@/components/service-discovery-panel";

describe("ServiceDiscoveryPanel", () => {
  const services = [{
    name: "api",
    instances: [
      { instance_id: "api-1", service_name: "api", address: "10.0.0.1:8080", status: "healthy", tags: ["v2"] },
      { instance_id: "api-2", service_name: "api", address: "10.0.0.2:8080", status: "unhealthy", tags: [] },
    ],
  }];
  it("renders", () => {
    const { container } = render(<ServiceDiscoveryPanel services={services} />);
    expect(container.textContent).toContain("Service Registry");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("1/2 healthy");
    expect(container.textContent).toContain("10.0.0.1:8080");
    expect(container.textContent).toContain("v2");
  });
});
