import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ModalShell } from "@/components/modal-shell";

describe("ModalShell", () => {
  it("renders modal", () => {
    const onClose = vi.fn();
    const onConfirm = vi.fn();
    const { container, getByText } = render(
      <ModalShell title="Delete App" size="sm" closable={true} hasFooter={true}
        onClose={onClose} onConfirm={onConfirm}>
        <p>Are you sure?</p>
      </ModalShell>
    );
    expect(container.textContent).toContain("Delete App");
    expect(container.textContent).toContain("Are you sure?");
    fireEvent.click(getByText("Confirm"));
    expect(onConfirm).toHaveBeenCalled();
    fireEvent.click(getByText("✕"));
    expect(onClose).toHaveBeenCalled();
  });
});
