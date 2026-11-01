import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CanaryReleaseCard from "../src/components/canary-release-card";

const activeRelease = {
  release_id: "r1",
  stable_version: "1.0.0",
  canary_version: "1.1.0",
  traffic_pct: 10,
  status: "active" as const,
  stable_error_rate: 1.0,
  canary_error_rate: 1.2,
  stable_latency_ms: 45,
  canary_latency_ms: 52,
};

const promotedRelease = { ...activeRelease, status: "promoted" as const, traffic_pct: 100 };

describe("CanaryReleaseCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<CanaryReleaseCard release={activeRelease} appName="My App" />);
    expect(container.textContent).toContain("Canary Release");
    expect(container.textContent).toContain("My App");
  });

  it("shows status badge", () => {
    const { container } = render(<CanaryReleaseCard release={activeRelease} appName="App" />);
    expect(container.textContent).toContain("Active");
  });

  it("shows promoted status", () => {
    const { container } = render(<CanaryReleaseCard release={promotedRelease} appName="App" />);
    expect(container.textContent).toContain("Promoted");
  });

  it("shows version labels", () => {
    const { container } = render(<CanaryReleaseCard release={activeRelease} appName="App" />);
    expect(container.textContent).toContain("Stable 1.0.0");
    expect(container.textContent).toContain("Canary 1.1.0");
  });

  it("shows traffic percentages", () => {
    const { container } = render(<CanaryReleaseCard release={activeRelease} appName="App" />);
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("10%");
  });

  it("shows error rates", () => {
    const { container } = render(<CanaryReleaseCard release={activeRelease} appName="App" />);
    expect(container.textContent).toContain("1.0% err");
    expect(container.textContent).toContain("1.2% err");
  });

  it("shows latency", () => {
    const { container } = render(<CanaryReleaseCard release={activeRelease} appName="App" />);
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("52ms");
  });
});
