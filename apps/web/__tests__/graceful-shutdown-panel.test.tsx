import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GracefulShutdownPanel } from "@/components/graceful-shutdown-panel";

const mockState = {
  phase: "cleanup" as const, hooksExecuted: 5, hooksFailed: 1,
  resourcesCleaned: ["connections", "timers", "cache"], durationMs: 2500,
};

describe("GracefulShutdownPanel", () => {
  it("renders shutdown state", () => {
    const { container } = render(<GracefulShutdownPanel state={mockState} />);
    expect(container.textContent).toContain("Cleanup");
    expect(container.textContent).toContain("2500ms");
    expect(container.textContent).toContain("5");
  });

  it("calls onShutdown", () => {
    const onShutdown = vi.fn();
    const { getByText } = render(<GracefulShutdownPanel state={null} onShutdown={onShutdown} />);
    fireEvent.click(getByText("Graceful"));
    expect(onShutdown).toHaveBeenCalled();
  });

  it("calls onForceKill", () => {
    const onForce = vi.fn();
    const { getByText } = render(<GracefulShutdownPanel state={null} onForceKill={onForce} />);
    fireEvent.click(getByText("Force Kill"));
    expect(onForce).toHaveBeenCalled();
  });
});
