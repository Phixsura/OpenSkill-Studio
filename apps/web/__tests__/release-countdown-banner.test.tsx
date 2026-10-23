import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseCountdownBanner } from "@/components/release-countdown-banner";

describe("ReleaseCountdownBanner", () => {
  it("countdown", () => {
    const { container } = render(
      <ReleaseCountdownBanner appName="AuthSDK" version="3.0" daysRemaining={14}
        hoursRemaining={6} isReleased={false} features={["Dark mode", "SSO"]} featureCount={2} />
    );
    expect(container.textContent).toContain("AuthSDK v3.0");
    expect(container.textContent).toContain("14");
    expect(container.textContent).toContain("Days");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("Coming Soon");
  });
  it("released", () => {
    const { container } = render(
      <ReleaseCountdownBanner appName="App" version="1.0" daysRemaining={0}
        hoursRemaining={0} isReleased={true} features={[]} featureCount={0} />
    );
    expect(container.textContent).toContain("🎉");
    expect(container.textContent).toContain("is Live!");
  });
});
