import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RuntimeEnvDashboard } from "@/components/runtime-env-dashboard";

const mockEnvs = [
  { id: "e1", extensionId: "ext-1", runtime: "node20", state: "running" as const,
    limits: { cpu: 1, memoryMb: 512, diskMb: 1024, networkEnabled: true },
    entrypoint: "index.js", uptimeSeconds: 3665, startedAt: "2024-01-01" },
  { id: "e2", extensionId: "ext-1", runtime: "python3.12", state: "stopped" as const,
    limits: { cpu: 0.5, memoryMb: 256, diskMb: 512, networkEnabled: false },
    entrypoint: "main.py", uptimeSeconds: 0 },
];

describe("RuntimeEnvDashboard", () => {
  it("renders environments with state", () => {
    const { container } = render(<RuntimeEnvDashboard environments={mockEnvs} />);
    expect(container.textContent).toContain("node20");
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("1/2 running");
  });

  it("shows start button for stopped envs", () => {
    const onStart = vi.fn();
    const { getByText } = render(<RuntimeEnvDashboard environments={mockEnvs} onStart={onStart} />);
    fireEvent.click(getByText("Start"));
    expect(onStart).toHaveBeenCalledWith("e2");
  });

  it("shows stop button for running envs", () => {
    const onStop = vi.fn();
    const { getByText } = render(<RuntimeEnvDashboard environments={mockEnvs} onStop={onStop} />);
    fireEvent.click(getByText("Stop"));
    expect(onStop).toHaveBeenCalledWith("e1");
  });

  it("formats uptime correctly", () => {
    const { container } = render(<RuntimeEnvDashboard environments={mockEnvs} />);
    expect(container.textContent).toContain("1h 1m");
  });
});
