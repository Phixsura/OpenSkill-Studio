import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ResponseCacheCard from "../src/components/response-cache-card";

const stats = { hits: 1500, misses: 300, hit_rate: 83.3, entries: 42 };
const entries = [
  { cache_key: "a1b2c3d4", status_code: 200, etag: "abc123", expires_in_seconds: 120 },
  { cache_key: "e5f6g7h8", status_code: 404, etag: "def456", expires_in_seconds: 30 },
];

describe("ResponseCacheCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <ResponseCacheCard stats={stats} recentEntries={entries} appName="My App" />,
    );
    expect(container.textContent).toContain("Response Cache");
    expect(container.textContent).toContain("My App");
  });

  it("shows hit rate", () => {
    const { container } = render(
      <ResponseCacheCard stats={stats} recentEntries={[]} appName="App" />,
    );
    expect(container.textContent).toContain("83.3% hit rate");
  });

  it("shows hit and miss counts", () => {
    const { container } = render(
      <ResponseCacheCard stats={stats} recentEntries={[]} appName="App" />,
    );
    expect(container.textContent).toContain("1.5K");
    expect(container.textContent).toContain("300");
    expect(container.textContent).toContain("Hits");
    expect(container.textContent).toContain("Misses");
  });

  it("shows cached entry count", () => {
    const { container } = render(
      <ResponseCacheCard stats={stats} recentEntries={[]} appName="App" />,
    );
    expect(container.textContent).toContain("42");
    expect(container.textContent).toContain("Cached");
  });

  it("renders recent entries", () => {
    const { container } = render(
      <ResponseCacheCard stats={stats} recentEntries={entries} appName="App" />,
    );
    expect(container.textContent).toContain("a1b2c3d4");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("120s TTL");
  });
});
