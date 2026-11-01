import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppCardV2 } from "@/components/app-card-v2";

describe("AppCardV2", () => {
  it("renders app card", () => {
    const { container } = render(
      <AppCardV2 name="SuperApp" description="A great app" category="connector" developerName="DevCo"
        rating={4.5} reviewCount={50} installCount={2000} badges={[{ type: "verified", label: "Verified", icon: "✅" }]}
        price="Free" slug="super-app" />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("DevCo");
    expect(container.textContent).toContain("2,000 installs");
    expect(container.textContent).toContain("Verified");
    expect(container.querySelector("a")?.getAttribute("href")).toBe("/marketplace/apps/super-app");
  });
});
