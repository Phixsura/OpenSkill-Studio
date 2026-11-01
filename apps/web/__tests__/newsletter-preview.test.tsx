import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NewsletterPreview } from "@/components/newsletter-preview";

describe("NewsletterPreview", () => {
  it("renders newsletter", () => {
    const { container } = render(
      <NewsletterPreview subject="Weekly #42" readTimeMin={2} footer="Unsubscribe"
        sections={[
          { type: "hero", title: "SSO Support", body: "Enterprise auth", cta: "Learn More", link: "" },
          { type: "text", title: "Updates", body: "15 new features", cta: "", link: "" },
        ]} />
    );
    expect(container.textContent).toContain("Weekly #42");
    expect(container.textContent).toContain("SSO Support");
    expect(container.textContent).toContain("Learn More →");
    expect(container.textContent).toContain("15 new features");
    expect(container.textContent).toContain("Unsubscribe");
  });
});
