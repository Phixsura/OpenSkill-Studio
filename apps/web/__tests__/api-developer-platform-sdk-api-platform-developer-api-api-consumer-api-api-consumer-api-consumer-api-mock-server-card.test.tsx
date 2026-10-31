import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-mock-server-card";

describe("ConsumerApiMockServerCard", () => {
  it("shows routes", () => {
    const routes = [{ id: "r1", method: "GET", pattern: "/api/users/*", status: 200, enabled: true, callCount: 42 }];
    const { container } = render(<Card routes={routes} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Mock Server");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users/*");
    expect(container.textContent).toContain("42 calls");
  });
  it("shows empty", () => {
    const { container } = render(<Card routes={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No mock routes");
  });
});
