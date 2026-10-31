import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-discovery-card";

describe("EndpointDiscoveryCard", () => {
  it("shows discovered endpoints", () => {
    const endpoints = [{ path: "/api/users", method: "GET", requestCount: 5000, avgMs: 75, status: "discovered", firstSeen: "2026-06-01" }];
    const { container } = render(<Card endpoints={endpoints} totalDiscovered={10} documented={6} undocumented={4} newCount={2} appName="App" />);
    expect(container.textContent).toContain("Endpoint Discovery");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("discovered");
    expect(container.textContent).toContain("4 undocumented");
    expect(container.textContent).toContain("2 new");
  });
  it("shows empty", () => {
    const { container } = render(<Card endpoints={[]} totalDiscovered={0} documented={0} undocumented={0} newCount={0} appName="App" />);
    expect(container.textContent).toContain("No endpoints discovered");
  });
});
