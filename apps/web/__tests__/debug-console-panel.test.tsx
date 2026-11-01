import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DebugConsolePanel } from "@/components/debug-console-panel";

describe("DebugConsolePanel", () => {
  it("renders console", () => {
    const { container } = render(
      <DebugConsolePanel total={3} breakpoints={2} onClear={vi.fn()}
        byLevel={{ info: 2, error: 1 }}
        output={[
          { level: "error", message: "Connection failed", source: "db" },
          { level: "info", message: "Server started", source: "main" },
        ]} />
    );
    expect(container.textContent).toContain("Debug Console");
    expect(container.textContent).toContain("3 logs");
    expect(container.textContent).toContain("2 bp");
    expect(container.textContent).toContain("Connection failed");
    expect(container.textContent).toContain("Server started");
    expect(container.textContent).toContain("info: 2");
  });
});
