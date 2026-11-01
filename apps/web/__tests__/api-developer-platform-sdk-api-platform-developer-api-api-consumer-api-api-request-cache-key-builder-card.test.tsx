import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-cache-key-builder-card";

describe("CacheKeyBuilderCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", prefix: "api", include_query: true, ignored_params: 2, header_count: 1 }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Cache Key Builder");
    expect(container.textContent).toContain("api:*");
    expect(container.textContent).toContain("2 ignored");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No cache key configs");
  });
});
