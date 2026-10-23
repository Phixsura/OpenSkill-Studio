import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LogStreamViewer } from "@/components/log-stream-viewer";

describe("LogStreamViewer", () => {
  const logs = [
    { timestamp: "2026-01-01T10:00:01Z", level: "info", icon: "ℹ️", color: "blue", message: "Server started", source: "" },
    { timestamp: "2026-01-01T10:00:05Z", level: "error", icon: "❌", color: "red", message: "DB connection failed", source: "" },
  ];
  it("renders logs", () => {
    const { container } = render(
      <LogStreamViewer logs={logs} errorCount={1} hasErrors={true} onFilterLevel={vi.fn()} onSearch={vi.fn()} />
    );
    expect(container.textContent).toContain("Log Stream");
    expect(container.textContent).toContain("Server started");
    expect(container.textContent).toContain("DB connection failed");
    expect(container.textContent).toContain("1 errors");
  });
});
