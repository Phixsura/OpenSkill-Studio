import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LogViewerPanel } from "@/components/log-viewer-panel";

describe("LogViewerPanel", () => {
  it("renders logs", () => {
    const logs = [
      { timestamp: "2026-01-01T10:00:00Z", level: "error", message: "Connection failed" },
      { timestamp: "2026-01-01T10:01:00Z", level: "info", message: "Reconnected" },
    ];
    const { container } = render(<LogViewerPanel logs={logs} onFilter={vi.fn()} />);
    expect(container.textContent).toContain("Connection failed");
    expect(container.textContent).toContain("Reconnected");
  });
  it("empty state", () => {
    const { container } = render(<LogViewerPanel logs={[]} onFilter={vi.fn()} />);
    expect(container.textContent).toContain("No logs found");
  });
});
