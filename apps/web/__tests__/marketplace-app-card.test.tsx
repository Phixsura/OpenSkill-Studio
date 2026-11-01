import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceAppCard } from "@/components/marketplace-app-card";

describe("MarketplaceAppCard", () => {
  it("renders card", () => {
    const onInstall = vi.fn();
    const { container, getByText } = render(
      <MarketplaceAppCard name="Slack Bot" description="Connect with Slack"
        icon="💬" category="communication" stars="⭐⭐⭐⭐☆"
        installDisplay="50,000" verified={true} priceDisplay="Free"
        developer="Acme" onInstall={onInstall} />
    );
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Connect with Slack");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("Acme");
    fireEvent.click(getByText("Install"));
    expect(onInstall).toHaveBeenCalled();
  });
});
