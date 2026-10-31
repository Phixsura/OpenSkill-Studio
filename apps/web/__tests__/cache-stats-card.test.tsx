import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CacheStatsCard from "../src/components/cache-stats-card";

const healthyStats = {
  hits: 9500,
  misses: 500,
  evictions: 120,
  size: 800,
  max_size: 1000,
  hit_rate: 95.0,
  namespaces: [
    { installation_id: "inst-1", entry_count: 500 },
    { installation_id: "inst-2", entry_count: 300 },
  ],
};

const emptyStats = {
  hits: 0,
  misses: 0,
  evictions: 0,
  size: 0,
  max_size: 1000,
  hit_rate: 0,
  namespaces: [],
};

const lowHitRate = {
  hits: 200,
  misses: 800,
  evictions: 50,
  size: 950,
  max_size: 1000,
  hit_rate: 20.0,
  namespaces: [{ installation_id: "inst-1", entry_count: 950 }],
};

describe("CacheStatsCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<CacheStatsCard stats={healthyStats} appName="My App" />);
    expect(container.textContent).toContain("Cache Stats");
    expect(container.textContent).toContain("My App");
  });

  it("shows hit rate percentage", () => {
    const { container } = render(<CacheStatsCard stats={healthyStats} appName="App" />);
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("hit rate");
  });

  it("shows hit and miss counts", () => {
    const { container } = render(<CacheStatsCard stats={healthyStats} appName="App" />);
    expect(container.textContent).toContain("9.5K");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("Hits");
    expect(container.textContent).toContain("Misses");
  });

  it("shows eviction count", () => {
    const { container } = render(<CacheStatsCard stats={healthyStats} appName="App" />);
    expect(container.textContent).toContain("120");
    expect(container.textContent).toContain("Evictions");
  });

  it("shows capacity bar", () => {
    const { container } = render(<CacheStatsCard stats={healthyStats} appName="App" />);
    expect(container.textContent).toContain("800");
    expect(container.textContent).toContain("1.0K");
    expect(container.textContent).toContain("Capacity");
  });

  it("renders namespace list", () => {
    const { container } = render(<CacheStatsCard stats={healthyStats} appName="App" />);
    expect(container.textContent).toContain("Namespaces");
    expect(container.textContent).toContain("inst-1: 500");
    expect(container.textContent).toContain("inst-2: 300");
  });

  it("hides namespaces when empty", () => {
    const { container } = render(<CacheStatsCard stats={emptyStats} appName="App" />);
    expect(container.textContent).not.toContain("Namespaces");
  });

  it("shows zero hit rate", () => {
    const { container } = render(<CacheStatsCard stats={emptyStats} appName="App" />);
    expect(container.textContent).toContain("0%");
  });
});
