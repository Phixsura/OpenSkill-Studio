import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UninstallConfirmation } from "@/components/uninstall-confirmation";

describe("UninstallConfirmation", () => {
  it("shows warning", () => {
    const { container } = render(<UninstallConfirmation appName="MyApp" onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("Uninstall MyApp?");
    expect(container.textContent).toContain("cannot be undone");
  });
  it("calls onConfirm", () => {
    const fn = vi.fn();
    const { container } = render(<UninstallConfirmation appName="X" onConfirm={fn} onCancel={vi.fn()} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Uninstall")!;
    fireEvent.click(btn);
    expect(fn).toHaveBeenCalled();
  });
  it("shows loading state", () => {
    const { container } = render(<UninstallConfirmation appName="X" onConfirm={vi.fn()} onCancel={vi.fn()} isLoading />);
    expect(container.textContent).toContain("Uninstalling...");
  });
});
