import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HelpCenterPage } from "@/components/help-center-page";

describe("HelpCenterPage", () => {
  const sections = [
    { id: "quickstart", title: "Quick Start", icon: "🚀", article_count: 5, description: "Get started" },
    { id: "sdk", title: "SDK Docs", icon: "📦", article_count: 12, description: "Reference" },
  ];
  it("renders", () => {
    const { container } = render(
      <HelpCenterPage sections={sections} totalArticles={17} onSearch={vi.fn()} onSectionClick={vi.fn()} />
    );
    expect(container.textContent).toContain("How can we help?");
    expect(container.textContent).toContain("17 articles");
    expect(container.textContent).toContain("Quick Start");
    expect(container.textContent).toContain("SDK Docs");
  });
  it("clicks section", () => {
    const fn = vi.fn();
    const { container } = render(
      <HelpCenterPage sections={sections} totalArticles={0} onSearch={vi.fn()} onSectionClick={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("quickstart");
  });
});
