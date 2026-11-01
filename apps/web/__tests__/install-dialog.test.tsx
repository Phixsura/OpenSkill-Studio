import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallDialog } from "@/components/install-dialog";

describe("InstallDialog", () => {
  it("renders scopes", () => {
    const { container } = render(
      <InstallDialog appName="TestApp" requiredScopes={["read", "write"]} onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Install TestApp");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("write");
  });

  it("confirm disabled until accepted", () => {
    const onConfirm = vi.fn();
    const { container } = render(
      <InstallDialog appName="App" requiredScopes={["admin"]} onConfirm={onConfirm} onCancel={vi.fn()} />
    );
    const installBtn = container.querySelector("button:last-child") as HTMLButtonElement;
    expect(installBtn.disabled).toBe(true);
    const checkbox = container.querySelector("input[type='checkbox']") as HTMLInputElement;
    fireEvent.click(checkbox);
    expect(installBtn.disabled).toBe(false);
  });

  it("cancel calls onCancel", () => {
    const onCancel = vi.fn();
    const { container } = render(
      <InstallDialog appName="App" requiredScopes={[]} onConfirm={vi.fn()} onCancel={onCancel} />
    );
    const cancelBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Cancel")!;
    fireEvent.click(cancelBtn);
    expect(onCancel).toHaveBeenCalled();
  });
});
