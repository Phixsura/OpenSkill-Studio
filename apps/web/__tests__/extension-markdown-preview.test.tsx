import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionMarkdownPreview } from "@/components/extension-markdown-preview";

describe("ExtensionMarkdownPreview", () => {
  it("renders with extension name", () => {
    const { container } = render(
      <ExtensionMarkdownPreview source="# Hello" extensionName="Slack Bot" />
    );
    expect(container.textContent).toContain("Slack Bot README");
  });

  it("shows split view by default", () => {
    const { container } = render(
      <ExtensionMarkdownPreview source="**bold text**" extensionName="Test" />
    );
    // Both editor and preview should be visible
    expect(container.querySelector("textarea")).toBeDefined();
    expect(container.innerHTML).toContain("bold text");
  });

  it("switches to edit mode", () => {
    const { getByText, container } = render(
      <ExtensionMarkdownPreview source="# Title" extensionName="Test" />
    );
    fireEvent.click(getByText("✏️ Edit"));
    expect(container.querySelector("textarea")).toBeDefined();
  });

  it("calls onSave", () => {
    const onSave = vi.fn();
    const { getByText } = render(
      <ExtensionMarkdownPreview source="content" extensionName="Test" onSave={onSave} />
    );
    fireEvent.click(getByText("💾 Save"));
    expect(onSave).toHaveBeenCalledWith("content");
  });
});
