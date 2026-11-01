import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperPortfolioCard } from "@/components/developer-portfolio-card";

const portfolio = {
  name: "Alice Chen", bio: "Full-stack extension developer", avatar: "",
  website: "https://alice.dev", github: "alicechen",
  extensions: 12, badges: 5, certifications: 2,
  totalInstalls: 50000, avgRating: 4.8,
};

describe("DeveloperPortfolioCard", () => {
  it("renders portfolio", () => {
    const { container } = render(<DeveloperPortfolioCard portfolio={portfolio} />);
    expect(container.textContent).toContain("Alice Chen");
    expect(container.textContent).toContain("Full-stack");
    expect(container.textContent).toContain("12");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("★ 4.8");
    expect(container.textContent).toContain("5 badges");
    expect(container.textContent).toContain("2 certs");
  });
});
