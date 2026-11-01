import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SocialProofBadges } from "@/components/social-proof-badges";

describe("SocialProofBadges", () => {
  const signals = [
    { type: "popular", icon: "🔥", text: "50K+ installs" },
    { type: "verified", icon: "✅", text: "Verified developer" },
  ];
  it("renders", () => {
    const { container } = render(<SocialProofBadges signals={signals} trustScore={80} />);
    expect(container.textContent).toContain("🔥");
    expect(container.textContent).toContain("50K+ installs");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("High trust score");
  });
  it("hidden when empty", () => {
    const { container } = render(<SocialProofBadges signals={[]} trustScore={0} />);
    expect(container.innerHTML).toBe("");
  });
});
