import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KeyboardShortcutsDialog } from "@/components/keyboard-shortcuts-dialog";

describe("KeyboardShortcutsDialog", () => {
  const byContext = {
    global: [{ combo: "Ctrl+K", action: "Search", context: "global", description: "" }],
    editor: [{ combo: "Ctrl+S", action: "Save", context: "editor", description: "" }],
  };
  it("renders grouped shortcuts", () => {
    const { container } = render(<KeyboardShortcutsDialog byContext={byContext} onClose={vi.fn()} />);
    expect(container.textContent).toContain("Keyboard Shortcuts");
    expect(container.textContent).toContain("global");
    expect(container.textContent).toContain("Ctrl+K");
    expect(container.textContent).toContain("Save");
  });
});
