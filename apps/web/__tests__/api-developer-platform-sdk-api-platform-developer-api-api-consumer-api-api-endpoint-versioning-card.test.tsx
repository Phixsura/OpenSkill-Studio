import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-endpoint-versioning-card";

describe("EndpointVersioningCard", () => {
  it("shows versions", () => {
    const endpoints = [{ endpoint: "/users", method: "GET", versions: [{ version: "v1", status: "deprecated", consumers_using: 10 }, { version: "v2", status: "active", consumers_using: 50 }], default_version: "v2" }];
    const { container } = render(<Card endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("Endpoint Versioning");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("v2");
  });
  it("shows empty", () => {
    const { container } = render(<Card endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No versioned endpoints");
  });
});
