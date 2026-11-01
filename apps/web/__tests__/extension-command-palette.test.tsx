import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionCommandPalette } from "@/components/extension-command-palette";

const mockCommands = [
  { id: "publish", label: "Publish Extension", icon: "🚀", category: "Actions", shortcut: "⌘P" },
  { id: "test", label: "Run Tests", icon: "🧪", category: "Actions", description: "Execute test suite" },
  { id: "settings", label: "Open Settings", icon: "⚙️", category: "Navigation" },
  { id: "docs", label: "View Documentation", icon: "📄", category: "Navigation" },
];

describe("ExtensionCommandPalette", () => {
  it("renders when open", () => {
    const { container } = render(
      <ExtensionCommandPalette commands={mockCommands} isOpen={true} />
    );
    expect(container.textContent).toContain("Publish Extension");
    expect(container.textContent).toContain("Run Tests");
    expect(container.textContent).toContain("⌘P");
  });

  it("does not render when closed", () => {
    const { container } = render(
      <ExtensionCommandPalette commands={mockCommands} isOpen={false} />
    );
    expect(container.textContent).not.toContain("Publish Extension");
  });

  it("filters by search", () => {
    const { container, getByPlaceholderText } = render(
      <ExtensionCommandPalette commands={mockCommands} isOpen={true} />
    );
    fireEvent.change(getByPlaceholderText("Type a command..."), { target: { value: "test" } });
    expect(container.textContent).toContain("Run Tests");
    expect(container.textContent).not.toContain("Open Settings");
  });

  it("calls onSelect", () => {
    const onSelect = vi.fn();
    const { getByText } = render(
      <ExtensionCommandPalette commands={mockCommands} isOpen={true} onSelect={onSelect} />
    );
    fireEvent.click(getByText("Open Settings"));
    expect(onSelect).toHaveBeenCalledWith("settings");
  });
});
