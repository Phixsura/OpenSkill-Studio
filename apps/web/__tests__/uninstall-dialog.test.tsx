import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UninstallDialog } from "@/components/uninstall-dialog";

describe("UninstallDialog", () => {
  it("shows app name", () => {
    const { container } = render(<UninstallDialog appName="My App" warnings={["Data lost"]} destructive={true} onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("Uninstall My App");
    expect(container.textContent).toContain("Data lost");
  });
  it("has buttons", () => {
    const { container } = render(<UninstallDialog appName="X" warnings={[]} destructive={false} onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("Cancel");
    expect(container.textContent).toContain("Uninstall");
  });
});
