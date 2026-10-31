import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-data-residency-card";

describe("DataResidencyCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", primary_region: "eu-west", allowed_regions: ["eu-west", "eu-central"], compliance_frameworks: ["gdpr"] }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Data Residency");
    expect(container.textContent).toContain("eu-west");
    expect(container.textContent).toContain("gdpr");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No residency configs");
  });
});
