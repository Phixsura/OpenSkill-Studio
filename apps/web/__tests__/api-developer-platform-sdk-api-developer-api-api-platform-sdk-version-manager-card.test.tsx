import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiPlatformSDKVersionManagerCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-platform-sdk-version-manager-card";

const versions = [
  { version: "2.0.0", language: "python", status: "stable", downloads: 50000, active_users: 500 },
  { version: "1.0.0", language: "python", status: "deprecated", downloads: 100000, active_users: 50 },
];

describe("Card", () => {
  it("shows SDK versions", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformSDKVersionManagerCard versions={versions} languages={["python", "javascript"]} deprecatedInUse={1} appName="App" />);
    expect(container.textContent).toContain("SDK Versions");
    expect(container.textContent).toContain("2 languages");
    expect(container.textContent).toContain("1 deprecated in use");
    expect(container.textContent).toContain("python");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("stable");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformSDKVersionManagerCard versions={[]} languages={[]} deprecatedInUse={0} appName="App" />);
    expect(container.textContent).toContain("No SDK versions");
  });
});
