import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SDKVersionTrackerCard from "../src/components/sdk-version-tracker-card";

const versions = [
  { version: "2.0.0", count: 50, is_latest: true },
  { version: "1.5.0", count: 30, is_latest: false },
  { version: "1.0.0", count: 10, is_latest: false },
];

describe("SDKVersionTrackerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <SDKVersionTrackerCard
        versions={versions}
        latestVersion="2.0.0"
        outdatedCount={40}
        totalInstallations={90}
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("SDK Versions");
    expect(container.textContent).toContain("My App");
  });

  it("shows latest version", () => {
    const { container } = render(
      <SDKVersionTrackerCard
        versions={versions}
        latestVersion="2.0.0"
        outdatedCount={0}
        totalInstallations={90}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("latest: v2.0.0");
  });

  it("shows outdated count", () => {
    const { container } = render(
      <SDKVersionTrackerCard
        versions={versions}
        latestVersion="2.0.0"
        outdatedCount={40}
        totalInstallations={90}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("40 outdated");
  });

  it("shows installation count", () => {
    const { container } = render(
      <SDKVersionTrackerCard
        versions={versions}
        latestVersion="2.0.0"
        outdatedCount={0}
        totalInstallations={90}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("90 installations tracked");
  });

  it("renders version bars", () => {
    const { container } = render(
      <SDKVersionTrackerCard
        versions={versions}
        latestVersion="2.0.0"
        outdatedCount={0}
        totalInstallations={90}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("v1.5.0");
    expect(container.textContent).toContain("50");
  });

  it("shows empty state", () => {
    const { container } = render(
      <SDKVersionTrackerCard
        versions={[]}
        latestVersion="1.0.0"
        outdatedCount={0}
        totalInstallations={0}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("No SDK usage recorded");
  });
});
