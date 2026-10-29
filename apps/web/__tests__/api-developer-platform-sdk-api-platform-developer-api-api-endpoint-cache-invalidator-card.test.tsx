import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-endpoint-cache-invalidator-card";

describe("CacheInvalidatorCard", () => {
  it("shows stats and invalidations", () => {
    const inv = [{ event_id: "i1", pattern: "/users*", reason: "update", invalidated_count: 5 }];
    const { container } = render(<Card stats={{ cached_entries: 50, total_hits: 1200 }} recentInvalidations={inv} appName="App" />);
    expect(container.textContent).toContain("Cache Invalidator");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("1,200");
    expect(container.textContent).toContain("5 cleared");
  });
  it("shows empty", () => {
    const { container } = render(<Card stats={{ cached_entries: 0, total_hits: 0 }} recentInvalidations={[]} appName="App" />);
    expect(container.textContent).toContain("Cache Invalidator");
  });
});
