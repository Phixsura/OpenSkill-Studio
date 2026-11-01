import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxConsole } from "@/components/sandbox-console";

const mockEntries = [
  { id: "1", type: "info" as const, text: "Sandbox ready", timestamp: "12:00" },
  { id: "2", type: "input" as const, text: "sdk.getExtension('ext-1')", timestamp: "12:01" },
  { id: "3", type: "output" as const, text: '{"name": "My Extension"}', timestamp: "12:01" },
  { id: "4", type: "error" as const, text: "TypeError: undefined is not a function", timestamp: "12:02" },
];

describe("SandboxConsole", () => {
  it("renders console with entries", () => {
    const { container } = render(
      <SandboxConsole entries={mockEntries} extensionName="Test Ext" />
    );
    expect(container.textContent).toContain("Sandbox Console");
    expect(container.textContent).toContain("Test Ext");
    expect(container.textContent).toContain("Sandbox ready");
    expect(container.textContent).toContain("TypeError");
    expect(container.textContent).toContain("4 entries");
  });

  it("calls onCommand on Enter", () => {
    const onCommand = vi.fn();
    const { getByPlaceholderText } = render(
      <SandboxConsole entries={[]} extensionName="Test" onCommand={onCommand} />
    );
    const input = getByPlaceholderText("Enter command...");
    fireEvent.change(input, { target: { value: "help" } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onCommand).toHaveBeenCalledWith("help");
  });

  it("shows empty state message", () => {
    const { container } = render(
      <SandboxConsole entries={[]} extensionName="Test" />
    );
    expect(container.textContent).toContain("Type a command");
  });
});
