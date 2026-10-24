import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KeyboardShortcutHelp } from "@/components/keyboard-shortcut-help";

describe("KeyboardShortcutHelp", () => {
  const shortcuts = [
    { key: "Cmd+K", action: "search", label: "Open Search", category: "navigation" },
    { key: "Cmd+N", action: "new_app", label: "New App", category: "actions" },
  ];
  it("renders", () => {
    const { container } = render(
      <KeyboardShortcutHelp shortcuts={shortcuts} categories={["navigation", "actions"]} onClose={vi.fn()} />
    );
    expect(container.textContent).toContain("Keyboard Shortcuts");
    expect(container.textContent).toContain("Open Search");
    expect(container.textContent).toContain("Cmd+K");
    expect(container.textContent).toContain("New App");
    expect(container.textContent).toContain("navigation");
  });
});
