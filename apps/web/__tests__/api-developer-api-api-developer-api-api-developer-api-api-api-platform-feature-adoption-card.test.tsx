import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiPlatformFeatureAdoptionCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-platform-feature-adoption-card";

const features = [
  { feature_name: "Webhooks", adoption_pct: 85, adopters: 85, total_consumers: 100, adoption_tier: "mainstream" },
  { feature_name: "GraphQL", adoption_pct: 15, adopters: 15, total_consumers: 100, adoption_tier: "early_adopters" },
];

describe("Card", () => {
  it("shows adoption", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiPlatformFeatureAdoptionCard features={features} tierCounts={{ mainstream: 1, early_adopters: 1 }} appName="App" />);
    expect(container.textContent).toContain("Feature Adoption");
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("85%");
    expect(container.textContent).toContain("mainstream: 1");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiPlatformFeatureAdoptionCard features={[]} tierCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No adoption data");
  });
});
