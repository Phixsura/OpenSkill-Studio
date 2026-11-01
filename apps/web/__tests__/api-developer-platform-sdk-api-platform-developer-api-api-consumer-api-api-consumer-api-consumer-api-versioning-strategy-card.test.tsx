import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-versioning-strategy-card";

describe("ConsumerApiVersioningStrategyCard", () => {
  it("shows versions and pinned", () => {
    const versions = [{ version: "v1", status: "deprecated", releasedAt: "2025-01" }, { version: "v2", status: "active", releasedAt: "2026-01" }];
    const { container } = render(<Card versions={versions} strategyType="path" defaultVersion="v2" pinnedVersion="v1" appName="App" />);
    expect(container.textContent).toContain("API Versioning");
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("Pinned to v1");
    expect(container.textContent).toContain("path");
  });
  it("shows empty", () => {
    const { container } = render(<Card versions={[]} strategyType="header" defaultVersion="v1" pinnedVersion={null} appName="App" />);
    expect(container.textContent).toContain("No versions");
  });
});
