import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CommandPalette } from "@/components/command-palette";

describe("CommandPalette", () => {
  const commands = [
    { id: "create", label: "Create App", shortcut: "Ctrl+N", category: "apps", icon: "➕" },
    { id: "logs", label: "View Logs", shortcut: "Ctrl+L", category: "debug", icon: "📋" },
  ];
  it("renders commands", () => {
    const { container } = render(<CommandPalette commands={commands} onSelect={vi.fn()} onClose={vi.fn()} />);
    expect(container.textContent).toContain("Create App");
    expect(container.textContent).toContain("Ctrl+N");
  });
  it("selects command", () => {
    const fn = vi.fn();
    const { container } = render(<CommandPalette commands={commands} onSelect={fn} onClose={vi.fn()} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[0]);
    expect(fn).toHaveBeenCalledWith("create");
  });
});
