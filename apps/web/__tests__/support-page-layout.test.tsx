import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SupportPageLayout } from "@/components/support-page-layout";

describe("SupportPageLayout", () => {
  it("renders support page", () => {
    const sections = [
      { key: "faq", title: "FAQ (2)", icon: "❓", items: [{ question: "How?", answer: "Like this." }] },
      { key: "contact", title: "Contact", icon: "📧", email: "help@app.com", response_time: "24h" },
    ];
    const { container } = render(<SupportPageLayout appName="MyApp" sections={sections} />);
    expect(container.textContent).toContain("MyApp Support");
    expect(container.textContent).toContain("How?");
    expect(container.textContent).toContain("help@app.com");
    expect(container.textContent).toContain("24h");
  });
});
