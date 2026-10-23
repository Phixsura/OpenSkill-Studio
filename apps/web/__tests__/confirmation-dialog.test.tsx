import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfirmationDialog } from "@/components/confirmation-dialog";

describe("ConfirmationDialog", () => {
  it("renders danger", () => {
    const { container } = render(
      <ConfirmationDialog title="Delete App?" icon="🗑️" message="This is permanent."
        danger={true} confirmText="DELETE" cancelLabel="Keep App"
        onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Delete App?");
    expect(container.textContent).toContain("🗑️");
    expect(container.textContent).toContain("This is permanent.");
    expect(container.textContent).toContain("Type DELETE to confirm");
    expect(container.textContent).toContain("Keep App");
    expect(container.textContent).toContain("Confirm");
  });
  it("non-danger no typing", () => {
    const { container } = render(
      <ConfirmationDialog title="Deploy?" icon="🚀" message="Deploy now?"
        danger={false} confirmText={null} cancelLabel="Cancel"
        onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.querySelector("input")).toBeFalsy();
  });
});
