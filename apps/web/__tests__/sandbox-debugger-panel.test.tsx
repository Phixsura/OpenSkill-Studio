import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxDebuggerPanel } from "@/components/sandbox-debugger-panel";

const mockState = { status: "running" as const, pid: "12345", uptime: "5m 23s", cpuPercent: 45, memoryMb: 128, memoryLimitMb: 256 };

const mockLogs = [
  { id: "1", level: "info" as const, message: "Extension started", timestamp: "12:00:01", source: "main" },
  { id: "2", level: "debug" as const, message: "Config loaded", timestamp: "12:00:02", source: "config" },
  { id: "3", level: "error" as const, message: "API timeout", timestamp: "12:00:05", source: "http" },
];

describe("SandboxDebuggerPanel", () => {
  it("renders status and resources", () => {
    const { container } = render(<SandboxDebuggerPanel logs={mockLogs} state={mockState} />);
    expect(container.textContent).toContain("Sandbox Debugger");
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("PID 12345");
    expect(container.textContent).toContain("45%");
    expect(container.textContent).toContain("128/256MB");
  });

  it("renders logs", () => {
    const { container } = render(<SandboxDebuggerPanel logs={mockLogs} state={mockState} />);
    expect(container.textContent).toContain("Extension started");
    expect(container.textContent).toContain("API timeout");
  });

  it("filters logs by level", () => {
    const { container, getByText } = render(<SandboxDebuggerPanel logs={mockLogs} state={mockState} />);
    fireEvent.click(getByText("error"));
    expect(container.textContent).toContain("API timeout");
    expect(container.textContent).not.toContain("Config loaded");
  });

  it("shows pause/stop for running sandbox", () => {
    const onPause = vi.fn();
    const { getByText } = render(<SandboxDebuggerPanel logs={mockLogs} state={mockState} onPause={onPause} />);
    fireEvent.click(getByText("⏸ Pause"));
    expect(onPause).toHaveBeenCalled();
  });
});
