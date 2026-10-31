import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-endpoint-canary-release-card";

describe("EndpointCanaryReleaseCard", () => {
  it("shows releases and analysis", () => {
    const releases = [{ id: "r1", endpoint: "/api/users", canaryVersion: "v2", stableVersion: "v1", weightPct: 10, status: "active" }];
    const analysis = { safeToPromote: true, errorDelta: 0.1, latencyDelta: 5, recommendation: "Safe to promote" };
    const { container } = render(<Card releases={releases} analysis={analysis} appName="App" />);
    expect(container.textContent).toContain("Canary Releases");
    expect(container.textContent).toContain("v1 → v2");
    expect(container.textContent).toContain("10% canary");
    expect(container.textContent).toContain("Safe to promote");
  });
  it("shows empty", () => {
    const { container } = render(<Card releases={[]} analysis={null} appName="App" />);
    expect(container.textContent).toContain("No canary releases");
  });
});
