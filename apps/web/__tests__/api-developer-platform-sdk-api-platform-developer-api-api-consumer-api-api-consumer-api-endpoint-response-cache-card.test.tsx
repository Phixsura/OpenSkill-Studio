import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-response-cache-card";

describe("EndpointResponseCacheCard", () => {
  it("shows caches", () => {
    const caches = [{ path: "/api/users", ttlSec: 60, entries: 25, hits: 150, varyBy: ["Accept-Language"] }];
    const { container } = render(<Card caches={caches} appName="App" />);
    expect(container.textContent).toContain("Response Cache");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("TTL: 60s");
    expect(container.textContent).toContain("25 entries");
    expect(container.textContent).toContain("150 hits");
    expect(container.textContent).toContain("Accept-Language");
  });
  it("shows empty", () => {
    const { container } = render(<Card caches={[]} appName="App" />);
    expect(container.textContent).toContain("No caches configured");
  });
});
