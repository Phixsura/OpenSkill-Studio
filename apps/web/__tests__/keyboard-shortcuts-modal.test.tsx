import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KeyboardShortcutsModal } from "@/components/keyboard-shortcuts-modal";

describe("KeyboardShortcutsModal", () => {
  it("renders shortcuts", () => {
    const onClose = vi.fn();
    const { container, getByText } = render(
      <KeyboardShortcutsModal onClose={onClose} categories={[
        { category: "navigation", shortcuts: [
          { keys: "⌘K", label: "Command Palette" },
          { keys: "⌘/", label: "Toggle Sidebar" },
        ]},
        { category: "actions", shortcuts: [
          { keys: "⌘⇧D", label: "Deploy" },
        ]},
      ]} />
    );
    expect(container.textContent).toContain("Keyboard Shortcuts");
    expect(container.textContent).toContain("navigation");
    expect(container.textContent).toContain("Command Palette");
    expect(container.textContent).toContain("⌘K");
    expect(container.textContent).toContain("Deploy");
    fireEvent.click(getByText("✕"));
    expect(onClose).toHaveBeenCalled();
  });
});
