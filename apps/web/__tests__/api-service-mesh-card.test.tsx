import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIServiceMeshCard from "../src/components/api-service-mesh-card";

const services = [
  { service_id: "api", name: "API", call_count: 500, error_rate: 1.0 },
  { service_id: "db", name: "Database", call_count: 450, error_rate: 10.0 },
];
const links = [{ source: "api", target: "db", call_count: 450 }];

describe("APIServiceMeshCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<APIServiceMeshCard services={services} links={links} appName="App" />);
    expect(container.textContent).toContain("Service Mesh");
    expect(container.textContent).toContain("2 services");
    expect(container.textContent).toContain("1 links");
  });

  it("shows service stats and links", () => {
    const { container } = render(<APIServiceMeshCard services={services} links={links} appName="App" />);
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("500 calls");
    expect(container.textContent).toContain("api → db");
  });

  it("shows empty state", () => {
    const { container } = render(<APIServiceMeshCard services={[]} links={[]} appName="App" />);
    expect(container.textContent).toContain("No services in mesh");
  });
});
