import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HelpArticleCard } from "@/components/help-article-card";

describe("HelpArticleCard", () => {
  it("renders", () => {
    const { container } = render(
      <HelpArticleCard title="Webhook Guide" category="guides" tags={["webhooks", "api"]}
        readTimeMin={3} url="/help/guides/webhook" onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Webhook Guide");
    expect(container.textContent).toContain("📖");
    expect(container.textContent).toContain("guides");
    expect(container.textContent).toContain("3 min read");
    expect(container.textContent).toContain("webhooks");
  });
  it("click", () => {
    const fn = vi.fn();
    const { container } = render(
      <HelpArticleCard title="X" category="faq" tags={[]} readTimeMin={1} url="/x" onClick={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
