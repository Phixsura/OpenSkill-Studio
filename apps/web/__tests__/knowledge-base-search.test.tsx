import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KnowledgeBaseSearch } from "@/components/knowledge-base-search";

describe("KnowledgeBaseSearch", () => {
  const articles = [
    { id: "1", title: "OAuth Guide", category: "auth", content: "How to implement OAuth", tags: ["oauth"] },
    { id: "2", title: "Webhooks", category: "webhooks", content: "Webhook setup", tags: ["webhooks"] },
  ];
  it("renders articles", () => {
    const { container } = render(<KnowledgeBaseSearch articles={articles} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("OAuth Guide");
    expect(container.textContent).toContain("Webhooks");
  });
  it("selects article", () => {
    const fn = vi.fn();
    const { container } = render(<KnowledgeBaseSearch articles={articles} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("1");
  });
});
