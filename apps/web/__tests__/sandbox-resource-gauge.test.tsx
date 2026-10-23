import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SandboxResourceGauge } from "@/components/sandbox-resource-gauge";

describe("SandboxResourceGauge", () => {
  const resources = [
    { usage_pct: 42.5, label: "CPU", current: "0.85 cores", limit: "2 cores" },
    { usage_pct: 50, label: "Memory", current: "256 MB", limit: "512 MB" },
  ];
  it("renders", () => {
    const { container } = render(
      <SandboxResourceGauge resources={resources} status="running" uptimeSec={3600} />
    );
    expect(container.textContent).toContain("Sandbox Resources");
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("1h 0m");
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("42.5%");
    expect(container.textContent).toContain("Memory");
  });
});
