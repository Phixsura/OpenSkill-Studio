import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RollbackDialog } from "@/components/rollback-dialog";

describe("RollbackDialog", () => {
  it("shows versions", () => {
    const { container } = render(
      <RollbackDialog appName="App" fromVersion="2.0" toVersion="1.0" onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("2.0 → 1.0");
    expect(container.textContent).toContain("Rollback App");
  });
  it("calls onConfirm", () => {
    const fn = vi.fn();
    const { container } = render(
      <RollbackDialog appName="X" fromVersion="2" toVersion="1" onConfirm={fn} onCancel={vi.fn()} />
    );
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Rollback")!;
    fireEvent.click(btn);
    expect(fn).toHaveBeenCalled();
  });
});
