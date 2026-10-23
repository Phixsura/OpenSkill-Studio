import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppDetailHero } from "@/components/app-detail-hero";

describe("AppDetailHero", () => {
  it("renders hero", () => {
    const { container } = render(
      <AppDetailHero appName="SuperApp" shortDescription="A great tool" category="connector"
        priceLabel="Free" developerName="DevCo" developerVerified={true}
        installs={2000} rating={4.5} reviews={100} version="2.0"
        badges={[{ label: "Popular" }]} ctaLabel="Install" ctaDisabled={false} onCta={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("DevCo");
    expect(container.textContent).toContain("2,000 installs");
    expect(container.textContent).toContain("4.5");
    expect(container.textContent).toContain("Popular");
    expect(container.textContent).toContain("Install");
  });
  it("install button", () => {
    const fn = vi.fn();
    const { container } = render(
      <AppDetailHero appName="X" shortDescription="" category="" priceLabel="" developerName=""
        developerVerified={false} installs={0} rating={0} reviews={0} version=""
        badges={[]} ctaLabel="Install" ctaDisabled={false} onCta={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
