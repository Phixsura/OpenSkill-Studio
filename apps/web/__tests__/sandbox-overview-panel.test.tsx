import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxOverviewPanel } from "@/components/sandbox-overview-panel";

const mockSandbox = {
  sandboxId: "sb-abc123", extensionId: "ext-1", runtime: "node20",
  state: "running" as const, cpuPercent: 45, memoryMb: 128,
  processCount: 3, timerCount: 5, kvEntries: 42, networkRequests: 150,
  uptime: "2h 30m",
};

describe("SandboxOverviewPanel", () => {
  it("renders sandbox info", () => {
    const { container } = render(<SandboxOverviewPanel sandbox={mockSandbox} />);
    expect(container.textContent).toContain("sb-abc123");
    expect(container.textContent).toContain("node20");
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("2h 30m");
  });

  it("shows resource metrics", () => {
    const { container } = render(<SandboxOverviewPanel sandbox={mockSandbox} />);
    expect(container.textContent).toContain("45%");
    expect(container.textContent).toContain("128MB");
    expect(container.textContent).toContain("42");
    expect(container.textContent).toContain("150");
  });

  it("shows stop button when running", () => {
    const onStop = vi.fn();
    const { getByText } = render(<SandboxOverviewPanel sandbox={mockSandbox} onStop={onStop} />);
    fireEvent.click(getByText("Stop"));
    expect(onStop).toHaveBeenCalled();
  });

  it("shows start button when stopped", () => {
    const onStart = vi.fn();
    const stopped = { ...mockSandbox, state: "stopped" as const };
    const { getByText } = render(<SandboxOverviewPanel sandbox={stopped} onStart={onStart} />);
    fireEvent.click(getByText("Start"));
    expect(onStart).toHaveBeenCalled();
  });
});
