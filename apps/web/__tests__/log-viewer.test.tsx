import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LogViewer } from "@/components/log-viewer";

describe("LogViewer", () => {
  const entries = [
    { raw: "App started", level: "INFO", icon: "ℹ️", timestamp: "10:00:00" },
    { raw: "Connection refused", level: "ERROR", icon: "❌", timestamp: "10:00:05" },
  ];
  it("renders entries", () => {
    const { container } = render(<LogViewer entries={entries} errorCount={1} />);
    expect(container.textContent).toContain("App started");
    expect(container.textContent).toContain("Connection refused");
    expect(container.textContent).toContain("ERROR (1)");
  });
  it("filters by level", () => {
    const { container } = render(<LogViewer entries={entries} errorCount={1} />);
    const errorBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("ERROR"))!;
    fireEvent.click(errorBtn);
    expect(container.textContent).toContain("Connection refused");
    expect(container.textContent).not.toContain("App started");
  });
});
