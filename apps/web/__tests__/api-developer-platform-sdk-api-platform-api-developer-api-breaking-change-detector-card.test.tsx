import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiDeveloperApiBreakingChangeDetectorCard from "../src/components/api-developer-platform-sdk-api-platform-api-developer-api-breaking-change-detector-card";

const changes = [{ change_id: "c1", endpoint: "/api/old", change_type: "endpoint_removed", description: "Removed legacy endpoint", affected_consumers: 50, severity: "critical" }];

describe("Card", () => {
  it("shows breaking changes", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiBreakingChangeDetectorCard changes={changes} criticalCount={1} totalAffected={50} appName="App" />);
    expect(container.textContent).toContain("Breaking Changes");
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("50 consumers affected");
    expect(container.textContent).toContain("/api/old");
    expect(container.textContent).toContain("endpoint_removed");
  });
  it("shows clean", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiBreakingChangeDetectorCard changes={[]} criticalCount={0} totalAffected={0} appName="App" />);
    expect(container.textContent).toContain("No breaking changes");
  });
});
