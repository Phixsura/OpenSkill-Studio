import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MarketplaceLandingPage from "@/app/(public)/marketplace/page";

describe("MarketplaceLandingPage", () => {
  it("renders without crashing", () => {
    const { container } = render(<MarketplaceLandingPage />);
    expect(container).toBeTruthy();
  });

  it("shows category links", () => {
    const { container } = render(<MarketplaceLandingPage />);
    const links = container.querySelectorAll("a");
    expect(links.length).toBeGreaterThanOrEqual(5);
  });

  it("contains Connectors category", () => {
    const { container } = render(<MarketplaceLandingPage />);
    expect(container.textContent).toContain("Connectors");
  });

  it("contains Automation category", () => {
    const { container } = render(<MarketplaceLandingPage />);
    expect(container.textContent).toContain("Automation");
  });

  it("contains Analytics category", () => {
    const { container } = render(<MarketplaceLandingPage />);
    expect(container.textContent).toContain("Analytics");
  });
});
