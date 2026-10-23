import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CommandPaletteModal } from "@/components/command-palette-modal";

describe("CommandPaletteModal", () => {
  const commands = [
    { id: "search", label: "Search Apps", shortcut: "Cmd+K", category: "nav", icon: "🔍" },
    { id: "deploy", label: "Deploy App", shortcut: "Cmd+D", category: "actions", icon: "🚀" },
  ];
  it("renders", () => {
    const { container } = render(<CommandPaletteModal commands={commands} onSelect={vi.fn()} onClose={vi.fn()} />);
    expect(container.textContent).toContain("Search Apps");
    expect(container.textContent).toContain("Deploy App");
    expect(container.textContent).toContain("Cmd+K");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(<CommandPaletteModal commands={commands} onSelect={fn} onClose={vi.fn()} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[0]);
    expect(fn).toHaveBeenCalledWith("search");
  });
});
