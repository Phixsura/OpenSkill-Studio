import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SocialProofSection } from "@/components/social-proof-section";

describe("SocialProofSection", () => {
  const testimonials = [{ quote: "Amazing!", author: "Alice", role: "CTO", company: "Acme" }];
  const stats = { developers: "1,800+", apps: "5,200+" };
  it("renders social proof", () => {
    const { container } = render(<SocialProofSection testimonials={testimonials} stats={stats} />);
    expect(container.textContent).toContain("Amazing!");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("CTO at Acme");
    expect(container.textContent).toContain("1,800+");
    expect(container.textContent).toContain("5,200+");
  });
});
