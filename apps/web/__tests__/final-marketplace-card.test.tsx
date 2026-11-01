import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FinalMarketplaceCard } from "@/components/final-marketplace-card";

describe("FinalMarketplaceCard", () => {
  it("renders card", () => {
    const onInstall = vi.fn();
    const { container, getByText } = render(
      <FinalMarketplaceCard name="Slack Bot" icon="💬" tagline="Best Slack"
        developer="Acme" stars="★★★★☆" installsDisplay="125,000" priceDisplay="Free"
        verified={true} category="communication" badges={["verified"]}
        onInstall={onInstall} onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Acme");
    expect(container.textContent).toContain("125,000");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("verified");
    fireEvent.click(getByText("Install"));
    expect(onInstall).toHaveBeenCalled();
  });
});
