import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiConsumerApiVersionAdoptionCard from "../src/components/api-developer-platform-sdk-api-consumer-api-version-adoption-card";

const adoptions = [
  { consumer_id: "acme", primary_version: "v2.0", using_latest: true, multi_version: false },
  { consumer_id: "beta", primary_version: "v1.0", using_latest: false, multi_version: true },
];

describe("Card", () => {
  it("shows adoption", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerApiVersionAdoptionCard adoptions={adoptions} versionDistribution={{ "v1.0": 5000, "v2.0": 50000 }} oldVersionCount={1} appName="App" />);
    expect(container.textContent).toContain("Version Adoption");
    expect(container.textContent).toContain("1 on old versions");
    expect(container.textContent).toContain("v1.0: 5,000");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("(multi)");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerApiVersionAdoptionCard adoptions={[]} versionDistribution={{}} oldVersionCount={0} appName="App" />);
    expect(container.textContent).toContain("No adoption data");
  });
});
