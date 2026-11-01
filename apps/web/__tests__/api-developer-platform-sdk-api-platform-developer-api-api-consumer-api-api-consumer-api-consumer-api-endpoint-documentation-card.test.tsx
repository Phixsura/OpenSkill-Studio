import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-endpoint-documentation-card";

describe("ConsumerApiEndpointDocumentationCard", () => {
  it("shows endpoints", () => {
    const endpoints = [{ id: "e1", method: "GET", path: "/api/users", summary: "List users", tags: ["users"], deprecated: false }];
    const { container } = render(<Card endpoints={endpoints} tags={["users"]} appName="App" />);
    expect(container.textContent).toContain("Endpoint Docs");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("List users");
  });
  it("shows empty", () => {
    const { container } = render(<Card endpoints={[]} tags={[]} appName="App" />);
    expect(container.textContent).toContain("No endpoints documented");
  });
});
