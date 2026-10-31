import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfirmationDialog } from "@/components/confirmation-dialog";

describe("ConfirmationDialog", () => {
  it("renders dialog", () => {
    const { container } = render(
      <ConfirmationDialog title="Delete App" message="This is permanent" icon="🗑️"
        severity="danger" confirmText="DELETE" requiresTextInput={true}
        onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Delete App");
    expect(container.textContent).toContain("This is permanent");
    expect(container.textContent).toContain("DELETE");
    expect(container.textContent).toContain("Cancel");
  });
});
