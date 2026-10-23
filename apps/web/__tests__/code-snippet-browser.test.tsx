import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CodeSnippetBrowser } from "@/components/code-snippet-browser";

describe("CodeSnippetBrowser", () => {
  it("renders snippets", () => {
    const onCopy = vi.fn();
    const { container, getAllByText } = render(
      <CodeSnippetBrowser onCopy={onCopy} snippets={[
        { id: "s1", title: "Auth middleware", language: "python", tags: ["auth"],
          preview: "def auth(req): ..." },
        { id: "s2", title: "React hook", language: "typescript", tags: ["react"],
          preview: "const useAuth = () => {}" },
      ]} />
    );
    expect(container.textContent).toContain("Code Snippets");
    expect(container.textContent).toContain("Auth middleware");
    expect(container.textContent).toContain("python");
    expect(container.textContent).toContain("React hook");
    fireEvent.click(getAllByText("Copy")[0]);
    expect(onCopy).toHaveBeenCalledWith("s1");
  });
});
