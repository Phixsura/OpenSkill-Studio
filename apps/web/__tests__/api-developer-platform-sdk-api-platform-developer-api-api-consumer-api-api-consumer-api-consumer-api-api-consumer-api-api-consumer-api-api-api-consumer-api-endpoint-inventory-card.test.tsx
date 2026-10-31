import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-endpoint-inventory-card";

describe("ConsumerApiEndpointInventoryCard", () => {
  it("shows inventory", () => {
    const endpoints = [{ id: "e1", method: "GET", path: "/api/users", status: "active", version: "v1" }];
    const summary = { total: 10, byMethod: { GET: 6, POST: 4 }, byStatus: { active: 8, deprecated: 2 } };
    const { container } = render(<Card endpoints={endpoints} summary={summary} appName="App" />);
    expect(container.textContent).toContain("Endpoint Inventory");
    expect(container.textContent).toContain("GET: 6");
    expect(container.textContent).toContain("/api/users");
  });
  it("shows empty", () => {
    const { container } = render(<Card endpoints={[]} summary={{ total: 0, byMethod: {}, byStatus: {} }} appName="App" />);
    expect(container.textContent).toContain("No endpoints");
  });
});
