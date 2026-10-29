import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiServiceRegistryCard from "../src/components/api-developer-api-api-developer-api-api-service-registry-card";

const services = [
  { service_id: "s1", name: "User Service", base_url: "https://users.com", version: "v2", status: "active", tags: ["core", "users"], stale: false },
  { service_id: "s2", name: "Legacy", base_url: "https://old.com", version: "v1", status: "active", tags: [], stale: true },
];

describe("APIDeveloperAPIApiDeveloperApiApiServiceRegistryCard", () => {
  it("shows registry", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiServiceRegistryCard services={services} staleCount={1} appName="App" />);
    expect(container.textContent).toContain("Service Registry");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("1 stale");
    expect(container.textContent).toContain("User Service");
    expect(container.textContent).toContain("core");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiServiceRegistryCard services={[]} staleCount={0} appName="App" />);
    expect(container.textContent).toContain("No registered services");
  });
});
