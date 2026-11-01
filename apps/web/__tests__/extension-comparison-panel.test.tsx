import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionComparisonPanel } from "@/components/extension-comparison-panel";

const exts = [
  { id: "a", name: "Slack Bot", rating: 4.8, installs: 10000, priceCents: 999, featureCount: 5, avgLatencyMs: 50 },
  { id: "b", name: "Discord Bot", rating: 4.5, installs: 8000, priceCents: 0, featureCount: 3, avgLatencyMs: 80 },
];
const winners = { rating: "a", installs: "a", price: "b", performance: "a" };
const matrix = { auth: { a: true, b: false }, webhooks: { a: true, b: true } };

describe("ExtensionComparisonPanel", () => {
  it("renders comparison table", () => {
    const { container } = render(
      <ExtensionComparisonPanel extensions={exts} winners={winners} recommended="a" featureMatrix={matrix} />
    );
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Recommended");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("Free");
  });
});
