import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SandboxLogViewer } from "@/components/sandbox-log-viewer";

describe("SandboxLogViewer", () => {
  it("renders empty state", () => {
    const { container } = render(<SandboxLogViewer logs={[]} />);
    expect(container.textContent).toContain("No logs");
  });

  it("renders log entries", () => {
    const logs = [
      { level: "info", message: "Started" },
      { level: "error", message: "Failed to connect" },
    ];
    const { container } = render(<SandboxLogViewer logs={logs} />);
    expect(container.textContent).toContain("Started");
    expect(container.textContent).toContain("Failed to connect");
  });

  it("renders all log levels", () => {
    const logs = ["info", "warn", "error", "debug"].map(level => ({ level, message: `${level} msg` }));
    const { container } = render(<SandboxLogViewer logs={logs} />);
    for (const l of logs) {
      expect(container.textContent).toContain(l.message);
    }
  });

  it("applies custom maxHeight", () => {
    const logs = [{ level: "info", message: "test" }];
    const { container } = render(<SandboxLogViewer logs={logs} maxHeight={500} />);
    const div = container.querySelector("div");
    expect(div?.style.maxHeight).toBe("500px");
  });
});
