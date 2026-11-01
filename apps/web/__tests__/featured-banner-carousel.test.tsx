import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeaturedBannerCarousel } from "@/components/featured-banner-carousel";

describe("FeaturedBannerCarousel", () => {
  it("renders banner", () => {
    const onCta = vi.fn();
    const { container, getByText } = render(
      <FeaturedBannerCarousel onCta={onCta} banners={[
        { title: "New: SSO", subtitle: "Enterprise auth", cta: "Enable", link: "/sso",
          bgGradient: "from-blue-600 to-purple-600", icon: "🔐" },
      ]} />
    );
    expect(container.textContent).toContain("New: SSO");
    expect(container.textContent).toContain("Enterprise auth");
    fireEvent.click(getByText("Enable"));
    expect(onCta).toHaveBeenCalledWith("/sso");
  });
});
