import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-version-negotiator-card";

describe("VersionNegotiatorCard", () => {
  it("shows versions", () => {
    const versions = [{ version: "v1", status: "stable", supported: true }, { version: "v2", status: "beta", supported: true }];
    const { container } = render(<Card versions={versions} defaultVersion="v1" deprecatedCount={0} appName="App" />);
    expect(container.textContent).toContain("API Versions");
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("stable");
    expect(container.textContent).toContain("default: v1");
  });
  it("shows deprecated count", () => {
    const { container } = render(<Card versions={[]} defaultVersion="v1" deprecatedCount={2} appName="App" />);
    expect(container.textContent).toContain("2 deprecated");
  });
});
