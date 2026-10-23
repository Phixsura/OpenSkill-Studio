import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallSnippetCopy } from "@/components/install-snippet-copy";

describe("InstallSnippetCopy", () => {
  const commands = { npm: "npm install pkg", yarn: "yarn add pkg", pnpm: "pnpm add pkg" };
  it("renders", () => {
    const { container } = render(
      <InstallSnippetCopy commands={commands} defaultManager="npm" onCopy={vi.fn()} />
    );
    expect(container.textContent).toContain("npm install pkg");
    expect(container.textContent).toContain("npm");
    expect(container.textContent).toContain("yarn");
    expect(container.textContent).toContain("pnpm");
    expect(container.textContent).toContain("Copy");
  });
  it("copy", () => {
    const fn = vi.fn();
    const { container } = render(
      <InstallSnippetCopy commands={commands} defaultManager="npm" onCopy={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Copy")!);
    expect(fn).toHaveBeenCalledWith("npm install pkg");
  });
});
