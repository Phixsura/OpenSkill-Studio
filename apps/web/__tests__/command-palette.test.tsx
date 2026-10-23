import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CommandPalette } from "@/components/command-palette";

describe("CommandPalette", () => {
  const cmds = [
    { id: "1", label: "New App", shortcut: "Ctrl+N", icon: "📄", category: "File" },
    { id: "2", label: "Deploy", shortcut: null, icon: "🚀", category: "Actions" },
  ];
  it("renders commands", () => {
    const { container } = render(<CommandPalette commands={cmds} onSelect={vi.fn()} onClose={vi.fn()} />);
    expect(container.textContent).toContain("New App");
    expect(container.textContent).toContain("Deploy");
    expect(container.textContent).toContain("Ctrl+N");
  });
  it("selects command", () => {
    const fn = vi.fn();
    const { container } = render(<CommandPalette commands={cmds} onSelect={fn} onClose={vi.fn()} />);
    const buttons = container.querySelectorAll("button");
    fireEvent.click(buttons[0]);
    expect(fn).toHaveBeenCalledWith("1");
  });
});
