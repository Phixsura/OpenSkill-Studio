import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-feature-adoption-card";

describe("ConsumerFeatureAdoptionCard", () => {
  it("shows features", () => {
    const features = [{ feature_id: "f1", name: "Webhooks", adoption_count: 45, adoption_pct: 90 }];
    const { container } = render(<Card features={features} totalConsumers={50} appName="App" />);
    expect(container.textContent).toContain("Feature Adoption");
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("45 (90%)");
  });
  it("shows empty", () => {
    const { container } = render(<Card features={[]} totalConsumers={0} appName="App" />);
    expect(container.textContent).toContain("No features tracked");
  });
});
