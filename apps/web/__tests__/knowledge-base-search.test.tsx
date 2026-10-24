import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KnowledgeBaseSearch } from "@/components/knowledge-base-search";

describe("KnowledgeBaseSearch", () => {
  const articles = [
    { id: "a1", title: "Webhooks Guide", category: "guides", tags: ["webhooks"] },
    { id: "a2", title: "API Auth", category: "guides", tags: ["auth"] },
  ];
  it("renders", () => {
    const { container } = render(
      <KnowledgeBaseSearch articles={articles} onSearch={vi.fn()} onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Help Center");
    expect(container.textContent).toContain("Webhooks Guide");
    expect(container.textContent).toContain("API Auth");
  });
  it("select article", () => {
    const fn = vi.fn();
    const { container } = render(
      <KnowledgeBaseSearch articles={articles} onSearch={vi.fn()} onSelect={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("a1");
  });
});
