import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ModalDialog } from "@/components/modal-dialog";

describe("ModalDialog", () => {
  it("renders modal", () => {
    const { container } = render(
      <ModalDialog title="Delete App" sizeClass="max-w-sm" closable={true}
        hasFooter={true} danger={true} onClose={vi.fn()} onConfirm={vi.fn()} confirmLabel="Delete">
        <p>Are you sure?</p>
      </ModalDialog>
    );
    expect(container.textContent).toContain("Delete App");
    expect(container.textContent).toContain("Are you sure?");
    expect(container.textContent).toContain("Cancel");
    expect(container.textContent).toContain("Delete");
  });
});
