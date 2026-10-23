import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CodeSnippetViewer } from "@/components/code-snippet-viewer";

describe("CodeSnippetViewer", () => {
  const languages = [
    { id: "typescript", code: 'import { OpenSkill } from "@openskill/sdk";' },
    { id: "python", code: 'from openskill import OpenSkill' },
  ];
  it("renders", () => {
    const { container } = render(<CodeSnippetViewer title="Install" languages={languages} onCopy={vi.fn()} />);
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("typescript");
    expect(container.textContent).toContain("python");
    expect(container.textContent).toContain("@openskill/sdk");
  });
  it("copy", () => {
    const fn = vi.fn();
    const { container } = render(<CodeSnippetViewer title="Install" languages={languages} onCopy={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Copy")!);
    expect(fn).toHaveBeenCalledWith(languages[0].code);
  });
});
