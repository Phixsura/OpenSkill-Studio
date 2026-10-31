import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiPlatformOperationalReadinessCard from "../src/components/api-developer-api-api-developer-api-api-platform-operational-readiness-card";

const checks = [
  { check_id: "c1", category: "security", name: "HTTPS enforced", required: true, passed: true },
  { check_id: "c2", category: "monitoring", name: "Alerting configured", required: true, passed: false },
];

describe("Card", () => {
  it("shows readiness", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiPlatformOperationalReadinessCard checks={checks} readinessPct={50} goNoGo="NO_GO" appName="App" />);
    expect(container.textContent).toContain("Operational Readiness");
    expect(container.textContent).toContain("NO GO");
    expect(container.textContent).toContain("HTTPS enforced");
    expect(container.textContent).toContain("required");
  });
});
