import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LogViewer } from "@/components/log-viewer";

const logs = [
  { logId: "l1", level: "info", message: "Server started", timestamp: Date.now() },
  { logId: "l2", level: "error", message: "Connection failed", timestamp: Date.now() },
];

describe("LogViewer", () => {
  it("renders logs", () => {
    const { container } = render(<LogViewer logs={logs} />);
    expect(container.textContent).toContain("Server started");
    expect(container.textContent).toContain("Connection failed");
    expect(container.textContent).toContain("info");
    expect(container.textContent).toContain("error");
  });
  it("empty state", () => {
    const { container } = render(<LogViewer logs={[]} />);
    expect(container.textContent).toContain("No logs");
  });
});
