import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LogViewerPanel } from "@/components/log-viewer-panel";

describe("LogViewerPanel", () => {
  const logs = [
    { level: "error", message: "Connection failed", timestamp: "12:00:00" },
    { level: "info", message: "Server started", timestamp: "11:59:00" },
  ];
  it("renders", () => {
    const { container } = render(<LogViewerPanel logs={logs} totalMatched={2} onFilter={vi.fn()} />);
    expect(container.textContent).toContain("Logs");
    expect(container.textContent).toContain("Connection failed");
    expect(container.textContent).toContain("Server started");
    expect(container.textContent).toContain("2 results");
  });
});
