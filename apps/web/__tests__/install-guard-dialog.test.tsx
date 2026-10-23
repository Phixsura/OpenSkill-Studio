import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallGuardDialog } from "@/components/install-guard-dialog";

describe("InstallGuardDialog", () => {
  it("can install", () => {
    const { container } = render(
      <InstallGuardDialog canInstall={true} blockers={[]} warnings={[]} onProceed={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Install");
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Install") as HTMLButtonElement;
    expect(btn.disabled).toBe(false);
  });
  it("blocked", () => {
    const { container } = render(
      <InstallGuardDialog canInstall={false} blockers={[{ type: "conflict", message: "Conflicts with AppX" }]}
        warnings={[]} onProceed={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Cannot Install");
    expect(container.textContent).toContain("Conflicts with AppX");
  });
  it("warning", () => {
    const { container } = render(
      <InstallGuardDialog canInstall={true} blockers={[]}
        warnings={[{ type: "admin", message: "Requires admin" }]} onProceed={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Requires admin");
  });
});
