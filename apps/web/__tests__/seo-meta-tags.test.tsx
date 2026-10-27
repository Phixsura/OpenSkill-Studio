import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SeoMetaTags } from "@/components/seo-meta-tags";

describe("SeoMetaTags", () => {
  it("renders preview", () => {
    const meta = { title: "Auth Plugin - OpenSkill Marketplace", description: "Secure authentication for your extensions", url: "https://marketplace.openskill.dev/ext/auth" };
    const { container } = render(<SeoMetaTags meta={meta} />);
    expect(container.textContent).toContain("Auth Plugin");
    expect(container.textContent).toContain("SEO Preview");
    expect(container.textContent).toContain("/60 chars");
  });
});
