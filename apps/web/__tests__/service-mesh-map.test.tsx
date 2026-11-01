import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ServiceMeshMap } from "@/components/service-mesh-map";

const services = [
  { serviceId: "auth", extensionId: "ext-1", url: "http://auth", circuitOpen: false, requestCount: 1000, errorCount: 2 },
  { serviceId: "db", extensionId: "ext-1", url: "http://db", circuitOpen: true, requestCount: 500, errorCount: 50 },
];

describe("ServiceMeshMap", () => {
  it("renders services", () => {
    const { container } = render(<ServiceMeshMap services={services} />);
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("CIRCUIT OPEN");
    expect(container.textContent).toContain("1/2 healthy");
  });
});
