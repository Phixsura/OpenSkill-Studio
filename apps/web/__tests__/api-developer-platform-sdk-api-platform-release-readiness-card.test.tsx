import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformReleaseReadinessCard from "../src/components/api-developer-platform-sdk-api-platform-release-readiness-card";

const checks = [
  { name: "Tests pass", passed: true, required: true },
  { name: "Security scan", passed: false, required: true },
  { name: "Docs updated", passed: true, required: false },
];

describe("Card", () => {
  it("shows readiness", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformReleaseReadinessCard version="v2.0" checks={checks} readinessPct={66.7} verdict="HOLD" appName="App" />);
    expect(container.textContent).toContain("Release Readiness");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("HOLD");
    expect(container.textContent).toContain("Tests pass");
    expect(container.textContent).toContain("required");
  });
});
