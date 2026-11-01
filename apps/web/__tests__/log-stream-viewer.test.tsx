import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LogStreamViewer } from "@/components/log-stream-viewer";

const mockEntries = [
  { id: "l1", level: "info" as const, message: "Server started", source: "stdout", timestamp: "12:00:01" },
  { id: "l2", level: "error" as const, message: "Connection refused", source: "stderr", timestamp: "12:00:05" },
  { id: "l3", level: "debug" as const, message: "Query executed", source: "stdout", timestamp: "12:00:06" },
];

describe("LogStreamViewer", () => {
  it("renders log entries", () => {
    const { container } = render(
      <LogStreamViewer entries={mockEntries} errorCount={1} />
    );
    expect(container.textContent).toContain("Server started");
    expect(container.textContent).toContain("Connection refused");
    expect(container.textContent).toContain("1 errors");
  });

  it("filters by level", () => {
    const { container } = render(
      <LogStreamViewer entries={mockEntries} errorCount={1} />
    );
    const select = container.querySelector("select");
    if (select) fireEvent.change(select, { target: { value: "error" } });
    expect(container.textContent).toContain("Connection refused");
    expect(container.textContent).not.toContain("Server started");
  });

  it("calls onClear", () => {
    const onClear = vi.fn();
    const { getByText } = render(
      <LogStreamViewer entries={mockEntries} errorCount={0} onClear={onClear} />
    );
    fireEvent.click(getByText("Clear"));
    expect(onClear).toHaveBeenCalled();
  });

  it("shows empty state", () => {
    const { container } = render(
      <LogStreamViewer entries={[]} errorCount={0} />
    );
    expect(container.textContent).toContain("No log entries");
  });
});
