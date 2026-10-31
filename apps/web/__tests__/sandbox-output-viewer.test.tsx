import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxOutputViewer } from "@/components/sandbox-output-viewer";

const mockBlocks = [
  { id: "1", type: "stdout" as const, content: "Starting extension...", timestamp: "12:00:01" },
  { id: "2", type: "result" as const, content: '{"status": "ok", "items": 42}', timestamp: "12:00:02", duration: 150 },
  { id: "3", type: "stderr" as const, content: "Warning: deprecated API call", timestamp: "12:00:03" },
  { id: "4", type: "metric" as const, content: "cpu: 12% | mem: 45MB | io: 3ops", timestamp: "12:00:04" },
];

describe("SandboxOutputViewer", () => {
  it("renders output blocks", () => {
    const { container } = render(
      <SandboxOutputViewer blocks={mockBlocks} extensionName="Test Ext" executionId="run-1" totalDuration={250} />
    );
    expect(container.textContent).toContain("Execution Output");
    expect(container.textContent).toContain("Test Ext");
    expect(container.textContent).toContain("250ms");
    expect(container.textContent).toContain("1 errors");
  });

  it("filters by type", () => {
    const { container, getByText } = render(
      <SandboxOutputViewer blocks={mockBlocks} extensionName="Test" executionId="r1" totalDuration={100} />
    );
    fireEvent.click(getByText("stderr"));
    expect(container.textContent).toContain("deprecated API");
    expect(container.textContent).not.toContain("Starting extension");
  });

  it("shows rerun button", () => {
    const onRerun = vi.fn();
    const { getByText } = render(
      <SandboxOutputViewer blocks={mockBlocks} extensionName="T" executionId="r1" totalDuration={100} onRerun={onRerun} />
    );
    fireEvent.click(getByText("🔄 Rerun"));
    expect(onRerun).toHaveBeenCalled();
  });
});
