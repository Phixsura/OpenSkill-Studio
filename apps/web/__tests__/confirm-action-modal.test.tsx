import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfirmActionModal } from "@/components/confirm-action-modal";

describe("ConfirmActionModal", () => {
  it("renders high danger", () => {
    const { container } = render(
      <ConfirmActionModal action="delete" resourceName="prod-db" message="Cannot undo."
        dangerLevel="high" requireTyping={true} confirmWord="PROD-DB"
        countdownSec={0} onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("delete prod-db?");
    expect(container.textContent).toContain("Cannot undo.");
    expect(container.textContent).toContain("PROD-DB");
    expect(container.querySelector("input")).toBeTruthy();
  });
  it("renders low danger", () => {
    const { container } = render(
      <ConfirmActionModal action="archive" resourceName="old" message="Sure?"
        dangerLevel="low" requireTyping={false} confirmWord={null}
        countdownSec={0} onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.querySelector("input")).toBeFalsy();
    expect(container.textContent).toContain("Confirm archive");
  });
});
