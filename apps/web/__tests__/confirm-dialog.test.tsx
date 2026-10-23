import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfirmDialog } from "@/components/confirm-dialog";

describe("ConfirmDialog", () => {
  it("renders dialog", () => {
    const onConfirm = vi.fn();
    const { container, getByText } = render(
      <ConfirmDialog title="Delete App?" body="This is permanent." confirmLabel="Delete"
        variant="danger" requiresName={false} resourceName="" onConfirm={onConfirm} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Delete App?");
    expect(container.textContent).toContain("This is permanent.");
    fireEvent.click(getByText("Delete"));
    expect(onConfirm).toHaveBeenCalled();
  });

  it("blocks confirm without name", () => {
    const onConfirm = vi.fn();
    const { getByText } = render(
      <ConfirmDialog title="Delete?" body="Type name" confirmLabel="Delete"
        variant="danger" requiresName={true} resourceName="myapp"
        onConfirm={onConfirm} onCancel={vi.fn()} />
    );
    const btn = getByText("Delete");
    fireEvent.click(btn);
    expect(onConfirm).not.toHaveBeenCalled(); // disabled
  });
});
