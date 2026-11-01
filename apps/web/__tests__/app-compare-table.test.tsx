import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppCompareTable } from "@/components/app-compare-table";

describe("AppCompareTable", () => {
  it("renders comparison", () => {
    const { container } = render(
      <AppCompareTable features={["sso", "webhooks"]} columns={[
        { name: "App A", icon: "📱", rating: 4.5, installs: 5000, price: "Free",
          featureValues: { sso: true, webhooks: true } },
        { name: "App B", icon: "🔧", rating: 4.0, installs: 3000, price: "$9/mo",
          featureValues: { sso: false, webhooks: true } },
      ]} />
    );
    expect(container.textContent).toContain("App A");
    expect(container.textContent).toContain("App B");
    expect(container.textContent).toContain("sso");
    expect(container.textContent).toContain("webhooks");
    expect(container.textContent).toContain("4.5");
    expect(container.textContent).toContain("$9/mo");
  });
});
