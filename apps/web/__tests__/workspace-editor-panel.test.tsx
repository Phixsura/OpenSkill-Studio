import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkspaceEditorPanel } from "@/components/workspace-editor-panel";

const mockWorkspace = {
  id: "ws-1", name: "My Extension", status: "active" as const,
  fileCount: 3, collaborators: ["dev-2"], owner: "dev-1",
};
const mockFiles = [
  { path: "src/index.ts", language: "typescript", size: 250 },
  { path: "package.json", language: "json", size: 120 },
  { path: "README.md", language: "markdown", size: 500 },
];

describe("WorkspaceEditorPanel", () => {
  it("renders workspace info", () => {
    const { container } = render(
      <WorkspaceEditorPanel workspace={mockWorkspace} files={mockFiles}
        selectedFile={null} fileContent="" />
    );
    expect(container.textContent).toContain("My Extension");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("1 collaborators");
  });

  it("shows file tree", () => {
    const { container } = render(
      <WorkspaceEditorPanel workspace={mockWorkspace} files={mockFiles}
        selectedFile={null} fileContent="" />
    );
    expect(container.textContent).toContain("src/index.ts");
    expect(container.textContent).toContain("package.json");
  });

  it("shows editor placeholder when no file selected", () => {
    const { container } = render(
      <WorkspaceEditorPanel workspace={mockWorkspace} files={mockFiles}
        selectedFile={null} fileContent="" />
    );
    expect(container.textContent).toContain("Select a file");
  });

  it("calls onSave", () => {
    const onSave = vi.fn();
    const { getByText } = render(
      <WorkspaceEditorPanel workspace={mockWorkspace} files={mockFiles}
        selectedFile="src/index.ts" fileContent="export default {}" onSave={onSave} />
    );
    fireEvent.click(getByText("Save"));
    expect(onSave).toHaveBeenCalled();
  });
});
