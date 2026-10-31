import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KbBrowser } from "@/components/kb-browser";

describe("KbBrowser", () => {
  it("renders articles", () => {
    const { container } = render(
      <KbBrowser total={10} categories={["guides", "api"]} onSelect={vi.fn()}
        articles={[
          { slug: "getting-started", title: "Getting Started", category: "guides", tags: ["setup"] },
          { slug: "api-auth", title: "API Auth", category: "api", tags: ["auth", "security"] },
        ]} />
    );
    expect(container.textContent).toContain("Knowledge Base");
    expect(container.textContent).toContain("10 articles");
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("guides");
    expect(container.textContent).toContain("API Auth");
    expect(container.textContent).toContain("auth");
  });
});
