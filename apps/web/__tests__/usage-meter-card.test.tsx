import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import UsageMeterCard from "../src/components/usage-meter-card";

const withinQuota = {
  metric: "api_calls",
  used: 450,
  limit: 1000,
  remaining: 550,
  usage_pct: 45,
  exceeded: false,
  window: "daily" as const,
};

const exceededQuota = {
  metric: "storage_bytes",
  used: 1200000,
  limit: 1000000,
  remaining: 0,
  usage_pct: 100,
  exceeded: true,
  window: "monthly" as const,
};

const noLimit = {
  metric: "webhook_events",
  used: 350,
  limit: null,
  remaining: null,
  usage_pct: null,
  exceeded: false,
  window: "hourly" as const,
};

const highUsage = {
  metric: "compute_ms",
  used: 8500,
  limit: 10000,
  remaining: 1500,
  usage_pct: 85,
  exceeded: false,
  window: "daily" as const,
};

describe("UsageMeterCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<UsageMeterCard metrics={[withinQuota]} appName="My App" />);
    expect(container.textContent).toContain("Usage Meter");
    expect(container.textContent).toContain("My App");
  });

  it("shows within-limits badge when all ok", () => {
    const { container } = render(<UsageMeterCard metrics={[withinQuota]} appName="App" />);
    expect(container.textContent).toContain("Within limits");
  });

  it("shows over-quota badge when exceeded", () => {
    const { container } = render(
      <UsageMeterCard metrics={[withinQuota, exceededQuota]} appName="App" />,
    );
    expect(container.textContent).toContain("1 over quota");
  });

  it("renders metric names with spaces", () => {
    const { container } = render(<UsageMeterCard metrics={[withinQuota]} appName="App" />);
    expect(container.textContent).toContain("api calls");
  });

  it("shows usage and limit for metered metric", () => {
    const { container } = render(<UsageMeterCard metrics={[withinQuota]} appName="App" />);
    expect(container.textContent).toContain("450");
    expect(container.textContent).toContain("1.0K");
    expect(container.textContent).toContain("remaining");
  });

  it("shows quota exceeded text", () => {
    const { container } = render(<UsageMeterCard metrics={[exceededQuota]} appName="App" />);
    expect(container.textContent).toContain("Quota exceeded");
  });

  it("shows no-limit label for unmetered metric", () => {
    const { container } = render(<UsageMeterCard metrics={[noLimit]} appName="App" />);
    expect(container.textContent).toContain("No limit");
    expect(container.textContent).toContain("350 used");
  });

  it("shows window label", () => {
    const { container } = render(<UsageMeterCard metrics={[withinQuota, noLimit]} appName="App" />);
    expect(container.textContent).toContain("today");
    expect(container.textContent).toContain("this hour");
  });

  it("formats large numbers", () => {
    const { container } = render(<UsageMeterCard metrics={[exceededQuota]} appName="App" />);
    expect(container.textContent).toContain("1.2M");
    expect(container.textContent).toContain("1.0M");
  });

  it("shows empty state", () => {
    const { container } = render(<UsageMeterCard metrics={[]} appName="App" />);
    expect(container.textContent).toContain("No metrics tracked");
  });
});
