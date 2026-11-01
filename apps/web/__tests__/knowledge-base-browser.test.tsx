import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KnowledgeBaseBrowser } from "@/components/knowledge-base-browser";

describe("KnowledgeBaseBrowser", () => {
  it("renders articles", () => {
    const onSelect = vi.fn();
    const { container, getAllByRole } = render(
      <KnowledgeBaseBrowser totalArticles={2} categories={["guides", "faq"]}
        onSelect={onSelect} articles={[
          { slug: "auth-guide", title: "Auth Guide", category: "guides", views: 150 },
          { slug: "webhooks-faq", title: "Webhooks FAQ", category: "faq", views: 80 },
        ]} />
    );
    expect(container.textContent).toContain("Knowledge Base");
    expect(container.textContent).toContain("2 articles");
    expect(container.textContent).toContain("Auth Guide");
    expect(container.textContent).toContain("150 views");
    fireEvent.click(getAllByRole("button")[0]);
    expect(onSelect).toHaveBeenCalledWith("auth-guide");
  });
});
