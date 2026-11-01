import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPISDKVersionTrackerCard from "../src/components/api-developer-api-sdk-version-tracker-card";

const versions = [
  { consumer_id: "c1", sdk_name: "sdk", sdk_version: "1.0", language: "python", request_count: 100 },
  { consumer_id: "c2", sdk_name: "sdk", sdk_version: "2.0", language: "node", request_count: 50 },
];

describe("APIDeveloperAPISDKVersionTrackerCard", () => {
  it("shows version data", () => {
    const { container } = render(<APIDeveloperAPISDKVersionTrackerCard versions={versions} outdatedCount={1} versionDistribution={{ "1.0": 1, "2.0": 1 }} appName="App" />);
    expect(container.textContent).toContain("SDK Version Tracker");
    expect(container.textContent).toContain("1 outdated");
    expect(container.textContent).toContain("v1.0: 1");
    expect(container.textContent).toContain("python");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPISDKVersionTrackerCard versions={[]} outdatedCount={0} versionDistribution={{}} appName="App" />);
    expect(container.textContent).toContain("No SDK usage tracked");
  });
});
