import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CommandPaletteModal } from "@/components/command-palette-modal";

describe("CommandPaletteModal", () => {
  it("renders commands", () => {
    const onSelect = vi.fn();
    const { container, getAllByRole } = render(
      <CommandPaletteModal onSearch={vi.fn()} onSelect={onSelect} commands={[
        { id: "dashboard", title: "Go to Dashboard", shortcut: "⌘D", category: "nav", icon: "🏠" },
        { id: "deploy", title: "Deploy", shortcut: "⌘⇧D", category: "actions", icon: "🚀" },
      ]} />
    );
    expect(container.textContent).toContain("Go to Dashboard");
    expect(container.textContent).toContain("⌘D");
    expect(container.textContent).toContain("Deploy");
    const buttons = getAllByRole("button");
    fireEvent.click(buttons[0]);
    expect(onSelect).toHaveBeenCalledWith("dashboard");
  });
});
