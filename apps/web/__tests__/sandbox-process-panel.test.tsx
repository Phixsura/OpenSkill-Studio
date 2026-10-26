import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxProcessPanel } from "@/components/sandbox-process-panel";

const mockProcs = [
  { pid: "p1", command: "node index.js", state: "running" as const, cpuPercent: 25, memoryMb: 128, startedAt: "" },
  { pid: "p2", command: "worker.py", state: "paused" as const, cpuPercent: 0, memoryMb: 64, startedAt: "" },
  { pid: "p3", command: "crashed-task", state: "crashed" as const, cpuPercent: 0, memoryMb: 0, startedAt: "", exitCode: 1 },
];

describe("SandboxProcessPanel", () => {
  it("renders processes with state", () => {
    const { container } = render(
      <SandboxProcessPanel processes={mockProcs} sandboxId="sb-1" />
    );
    expect(container.textContent).toContain("node index.js");
    expect(container.textContent).toContain("1 running");
    expect(container.textContent).toContain("25% CPU");
  });

  it("shows exit code for crashed", () => {
    const { container } = render(
      <SandboxProcessPanel processes={mockProcs} sandboxId="sb-1" />
    );
    expect(container.textContent).toContain("exit:1");
  });

  it("calls onKill", () => {
    const onKill = vi.fn();
    const { getByText } = render(
      <SandboxProcessPanel processes={mockProcs} sandboxId="sb-1" onKill={onKill} />
    );
    fireEvent.click(getByText("Kill"));
    expect(onKill).toHaveBeenCalledWith("p1");
  });

  it("calls onKillAll", () => {
    const onKillAll = vi.fn();
    const { getByText } = render(
      <SandboxProcessPanel processes={mockProcs} sandboxId="sb-1" onKillAll={onKillAll} />
    );
    fireEvent.click(getByText("Kill All"));
    expect(onKillAll).toHaveBeenCalled();
  });
});
