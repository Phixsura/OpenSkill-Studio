import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfirmDialog } from "@/components/confirm-dialog";

describe("ConfirmDialog", () => {
  it("shows title and message", () => {
    const { container } = render(<ConfirmDialog title="Delete App?" message="This cannot be undone" onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("Delete App?");
    expect(container.textContent).toContain("cannot be undone");
  });
  it("calls onConfirm", () => {
    const onConfirm = vi.fn();
    const { container } = render(<ConfirmDialog title="X" message="Y" onConfirm={onConfirm} onCancel={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Confirm")!);
    expect(onConfirm).toHaveBeenCalled();
  });
  it("calls onCancel", () => {
    const onCancel = vi.fn();
    const { container } = render(<ConfirmDialog title="X" message="Y" onConfirm={vi.fn()} onCancel={onCancel} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Cancel")!);
    expect(onCancel).toHaveBeenCalled();
  });
  it("shows destructive styling", () => {
    const { container } = render(<ConfirmDialog title="X" message="Y" destructive confirmLabel="Delete" onConfirm={vi.fn()} onCancel={vi.fn()} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Delete");
    expect(btn?.className).toContain("red");
  });
});
