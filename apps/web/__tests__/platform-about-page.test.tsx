import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformAboutPage } from "@/components/platform-about-page";

describe("PlatformAboutPage", () => {
  it("renders about", () => {
    const { container } = render(
      <PlatformAboutPage version="5.0.0" modules={10} commits={2406}
        lines={209000} files={6980} builder="Claude Opus 5" />
    );
    expect(container.textContent).toContain("OpenSkill Platform");
    expect(container.textContent).toContain("2,406");
    expect(container.textContent).toContain("209,000");
    expect(container.textContent).toContain("6,980");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
    expect(container.textContent).toContain("Claude Opus 5");
  });
});
