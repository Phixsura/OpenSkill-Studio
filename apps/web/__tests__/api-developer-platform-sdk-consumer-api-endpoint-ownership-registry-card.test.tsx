import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-ownership-registry-card";

describe("EndpointOwnershipRegistryCard", () => {
  it("shows ownership", () => {
    const owners = [{ endpoint: "/api/users", team: "backend", ownerEmail: "a@co.com", slaTier: "standard" }];
    const { container } = render(<Card owners={owners} byTeam={{ backend: 3, payments: 1 }} unownedCount={2} appName="App" />);
    expect(container.textContent).toContain("Endpoint Ownership");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("backend: 3");
    expect(container.textContent).toContain("2 unowned");
  });
  it("shows empty", () => {
    const { container } = render(<Card owners={[]} byTeam={{}} unownedCount={0} appName="App" />);
    expect(container.textContent).toContain("No ownership data");
  });
});
