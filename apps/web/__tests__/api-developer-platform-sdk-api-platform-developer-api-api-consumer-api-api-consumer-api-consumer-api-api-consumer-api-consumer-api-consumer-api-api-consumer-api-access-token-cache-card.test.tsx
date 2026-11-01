import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-consumer-api-api-consumer-api-access-token-cache-card";

describe("AccessTokenCacheCard", () => {
  it("shows cache stats", () => {
    const { container } = render(<Card totalEntries={500} hitCount={4500} missCount={500} hitRate={90} evictionCount={10} ttlSeconds={300} maxEntries={10000} appName="App" />);
    expect(container.textContent).toContain("Token Cache");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("10 evictions");
    expect(container.textContent).toContain("TTL: 300s");
  });
  it("shows no evictions", () => {
    const { container } = render(<Card totalEntries={100} hitCount={900} missCount={100} hitRate={90} evictionCount={0} ttlSeconds={60} maxEntries={1000} appName="App" />);
    expect(container.textContent).not.toContain("evictions");
  });
});
