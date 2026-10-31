import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-dependency-map-card";

describe("EndpointDependencyMapCard", () => {
  it("shows deps", () => {
    const deps = [{ from: "/orders", to: "/users", type: "calls", critical: true }];
    const { container } = render(<Card dependencies={deps} appName="App" />);
    expect(container.textContent).toContain("Dependency Map");
    expect(container.textContent).toContain("/orders");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("calls");
  });
  it("shows empty", () => {
    const { container } = render(<Card dependencies={[]} appName="App" />);
    expect(container.textContent).toContain("No dependencies");
  });
});
