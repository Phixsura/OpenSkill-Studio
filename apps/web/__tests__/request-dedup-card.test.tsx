import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RequestDedupCard from "../src/components/request-dedup-card";

const stats = { tracked: 100, total_duplicates: 25, ttl_seconds: 300 };

describe("RequestDedupCard", () => {
  it("renders header", () => {
    const { container } = render(<RequestDedupCard stats={stats} appName="My App" />);
    expect(container.textContent).toContain("Request Dedup");
  });

  it("shows TTL window", () => {
    const { container } = render(<RequestDedupCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("300s window");
  });

  it("shows tracked count", () => {
    const { container } = render(<RequestDedupCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("Tracked");
  });

  it("shows duplicate count", () => {
    const { container } = render(<RequestDedupCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("Duplicates");
  });

  it("shows dedup rate", () => {
    const { container } = render(<RequestDedupCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("20%");
    expect(container.textContent).toContain("Dedup Rate");
  });
});
