import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeaturedAppCarousel } from "@/components/featured-app-carousel";

const APPS = [
  { appId: "a1", name: "Cool Connector", description: "Connects everything", category: "connector", reason: "Editor's pick" },
  { appId: "a2", name: "Auto Grader", description: null, category: "automation" },
];

describe("FeaturedAppCarousel", () => {
  it("shows apps", () => {
    const { container } = render(<FeaturedAppCarousel apps={APPS} />);
    expect(container.textContent).toContain("Cool Connector");
    expect(container.textContent).toContain("Auto Grader");
  });

  it("shows reason", () => {
    const { container } = render(<FeaturedAppCarousel apps={APPS} />);
    expect(container.textContent).toContain("Editor's pick");
  });

  it("returns null for empty", () => {
    const { container } = render(<FeaturedAppCarousel apps={[]} />);
    expect(container.innerHTML).toBe("");
  });

  it("shows category icons", () => {
    const { container } = render(<FeaturedAppCarousel apps={APPS} />);
    expect(container.textContent).toContain("🔌");
  });
});
