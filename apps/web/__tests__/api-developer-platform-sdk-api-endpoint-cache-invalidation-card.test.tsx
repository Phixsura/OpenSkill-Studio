import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiEndpointCacheInvalidationCard from "../src/components/api-developer-platform-sdk-api-endpoint-cache-invalidation-card";

const rules = [{ rule_id: "r1", endpoint: "/api/users", trigger: "on_write", pattern: "users:*", invalidations: 500 }];

describe("Card", () => {
  it("shows rules", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiEndpointCacheInvalidationCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Cache Invalidation");
    expect(container.textContent).toContain("on_write");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("500×");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiEndpointCacheInvalidationCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No invalidation rules");
  });
});
