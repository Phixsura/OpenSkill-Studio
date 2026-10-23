import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StatusBadgeEmbed } from "@/components/status-badge-embed";

describe("StatusBadgeEmbed", () => {
  it("renders", () => {
    const { container } = render(
      <StatusBadgeEmbed badgeUrl="https://badge.dev/status.svg"
        markdownSnippet="![Status](url)" htmlSnippet='<img src="url">'
        onCopy={vi.fn()} />
    );
    expect(container.textContent).toContain("Status Badge");
    expect(container.textContent).toContain("markdown");
    expect(container.textContent).toContain("html");
    expect(container.textContent).toContain("![Status](url)");
  });
  it("copy", () => {
    const fn = vi.fn();
    const { container } = render(
      <StatusBadgeEmbed badgeUrl="x" markdownSnippet="md" htmlSnippet="ht" onCopy={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Copy")!);
    expect(fn).toHaveBeenCalledWith("md");
  });
});
