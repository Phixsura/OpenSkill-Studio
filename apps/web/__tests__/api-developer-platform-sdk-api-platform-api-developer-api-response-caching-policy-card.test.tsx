import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiDeveloperApiResponseCachingPolicyCard from "../src/components/api-developer-platform-sdk-api-platform-api-developer-api-response-caching-policy-card";

const policies = [
  { endpoint: "/api/users", ttl_seconds: 3600, cache_control: "public", is_cacheable: true, vary_headers: ["Accept"] },
  { endpoint: "/api/auth", ttl_seconds: 0, cache_control: "no-store", is_cacheable: false, vary_headers: [] },
];

describe("Card", () => {
  it("shows caching policies", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiResponseCachingPolicyCard policies={policies} cacheableCount={1} appName="App" />);
    expect(container.textContent).toContain("Caching Policies");
    expect(container.textContent).toContain("1/2 cacheable");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("public");
    expect(container.textContent).toContain("3600s");
    expect(container.textContent).toContain("no-store");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiResponseCachingPolicyCard policies={[]} cacheableCount={0} appName="App" />);
    expect(container.textContent).toContain("No caching policies");
  });
});
