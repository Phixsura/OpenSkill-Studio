import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppDetailHero } from "@/components/app-detail-hero";

describe("AppDetailHero", () => {
  it("renders hero", () => {
    const onInstall = vi.fn();
    const { container, getByText } = render(
      <AppDetailHero name="Slack Bot Pro" tagline="Ultimate Slack" icon="💬"
        developer="Acme" verified={true} stars="★★★★☆" reviewCount={342}
        installsDisplay="125,000" priceDisplay="Free" version="3.2.1"
        category="communication" tags={["slack", "automation"]} onInstall={onInstall} />
    );
    expect(container.textContent).toContain("Slack Bot Pro");
    expect(container.textContent).toContain("Ultimate Slack");
    expect(container.textContent).toContain("Verified");
    expect(container.textContent).toContain("125,000");
    expect(container.textContent).toContain("342 reviews");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("slack");
    fireEvent.click(getByText("Install"));
    expect(onInstall).toHaveBeenCalled();
  });
});
