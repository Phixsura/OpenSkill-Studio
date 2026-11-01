import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiEndpointDependencyMapperCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-endpoint-dependency-mapper-card";

const endpoints = [
  { endpoint: "/api/auth", dependency_count: 0, dependent_count: 8, is_critical: true },
  { endpoint: "/api/orders", dependency_count: 3, dependent_count: 1, is_critical: false },
];

describe("Card", () => {
  it("shows dependencies", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiEndpointDependencyMapperCard endpoints={endpoints} criticalCount={1} appName="App" />);
    expect(container.textContent).toContain("Endpoint Dependencies");
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("/api/auth");
    expect(container.textContent).toContain("8 dependents");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiEndpointDependencyMapperCard endpoints={[]} criticalCount={0} appName="App" />);
    expect(container.textContent).toContain("No dependencies mapped");
  });
});
