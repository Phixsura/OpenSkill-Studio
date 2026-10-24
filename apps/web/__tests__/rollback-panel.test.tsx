import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RollbackPanel } from "@/components/rollback-panel";

describe("RollbackPanel", () => {
  const options = [
    { version: "1.5.0", deployedAt: "2026-01-02", commit: "def456", author: "Bob" },
  ];
  it("renders options", () => {
    const { container } = render(
      <RollbackPanel current="2.0.0" options={options} canRollback={true} onRollback={vi.fn()} />
    );
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("v1.5.0");
    expect(container.textContent).toContain("Rollback");
  });
  it("rollback click", () => {
    const fn = vi.fn();
    const { container } = render(
      <RollbackPanel current="2.0.0" options={options} canRollback={true} onRollback={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("1.5.0");
  });
});
