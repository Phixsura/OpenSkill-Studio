import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KeyboardShortcutsDialog } from "@/components/keyboard-shortcuts-dialog";

describe("KeyboardShortcutsDialog", () => {
  const shortcuts = [
    { key: "Ctrl+K", label: "Command Palette", scope: "global" },
    { key: "Ctrl+N", label: "New App", scope: "dashboard" },
  ];
  it("renders shortcuts", () => {
    const { container } = render(<KeyboardShortcutsDialog shortcuts={shortcuts} onClose={vi.fn()} />);
    expect(container.textContent).toContain("Command Palette");
    expect(container.textContent).toContain("Ctrl+K");
    expect(container.textContent).toContain("global");
  });
  it("closes", () => {
    const fn = vi.fn();
    const { container } = render(<KeyboardShortcutsDialog shortcuts={shortcuts} onClose={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
