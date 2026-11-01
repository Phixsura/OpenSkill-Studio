import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionQuickActions } from "@/components/extension-quick-actions";

const mockActions = [
  { id: "publish", label: "Publish", icon: "🚀", description: "Publish new version", shortcut: "⌘P" },
  { id: "test", label: "Run Tests", icon: "🧪", description: "Execute test suite" },
  { id: "logs", label: "View Logs", icon: "📋", description: "Open log viewer", disabled: true },
  { id: "delete", label: "Delete", icon: "🗑️", description: "Remove extension", danger: true },
];

describe("ExtensionQuickActions", () => {
  it("renders actions with labels", () => {
    const { container } = render(
      <ExtensionQuickActions extensionName="Slack Bot" actions={mockActions} />
    );
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Publish");
    expect(container.textContent).toContain("Run Tests");
    expect(container.textContent).toContain("⌘P");
  });

  it("calls onAction when clicked", () => {
    const onAction = vi.fn();
    const { getByText } = render(
      <ExtensionQuickActions extensionName="Test" actions={mockActions} onAction={onAction} />
    );
    fireEvent.click(getByText("Publish"));
    expect(onAction).toHaveBeenCalledWith("publish");
  });

  it("does not fire disabled actions", () => {
    const onAction = vi.fn();
    const { getByText } = render(
      <ExtensionQuickActions extensionName="Test" actions={mockActions} onAction={onAction} />
    );
    fireEvent.click(getByText("View Logs"));
    expect(onAction).not.toHaveBeenCalled();
  });

  it("shows danger styling", () => {
    const { getByText } = render(
      <ExtensionQuickActions extensionName="Test" actions={mockActions} />
    );
    const deleteBtn = getByText("Delete").closest("button");
    expect(deleteBtn?.className).toContain("red");
  });
});
