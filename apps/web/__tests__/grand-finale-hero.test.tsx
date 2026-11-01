import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GrandFinaleHero } from "@/components/grand-finale-hero";

describe("GrandFinaleHero", () => {
  it("renders grand finale", () => {
    const { container } = render(<GrandFinaleHero />);
    expect(container.textContent).toContain("235K+");
    expect(container.textContent).toContain("8,000+");
    expect(container.textContent).toContain("2,724");
    expect(container.textContent).toContain("1,362+");
    expect(container.textContent).toContain("ALL SYSTEMS GREEN");
    expect(container.textContent).toContain("Fully Operational");
  });
});
