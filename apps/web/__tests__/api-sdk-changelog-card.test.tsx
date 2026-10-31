import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APISDKChangelogCard from "../src/components/api-sdk-changelog-card";

const entries = [
  { version: "2.0.0", changes: ["New auth", "Updated types"], breaking: true },
  { version: "1.5.0", changes: ["Bug fix"], breaking: false },
];

describe("APISDKChangelogCard", () => {
  it("shows versions", () => {
    const { container } = render(<APISDKChangelogCard entries={entries} appName="App" />);
    expect(container.textContent).toContain("SDK Changelog");
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("1 breaking");
    expect(container.textContent).toContain("2 changes");
  });
  it("shows empty", () => {
    const { container } = render(<APISDKChangelogCard entries={[]} appName="App" />);
    expect(container.textContent).toContain("No SDK versions");
  });
});
