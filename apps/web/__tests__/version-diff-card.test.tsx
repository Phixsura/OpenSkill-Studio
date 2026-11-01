import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import VersionDiffCard from "../src/components/version-diff-card";

const changes = [
  { path: "name", change_type: "modified" as const, old_value: "App v1", new_value: "App v2" },
  { path: "config.debug", change_type: "removed" as const, old_value: true },
  { path: "config.cache_ttl", change_type: "added" as const, new_value: 300 },
];

describe("VersionDiffCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <VersionDiffCard fromVersion="1.0.0" toVersion="2.0.0" changes={changes} appName="My App" />,
    );
    expect(container.textContent).toContain("Version Diff");
    expect(container.textContent).toContain("My App");
  });

  it("shows version range", () => {
    const { container } = render(
      <VersionDiffCard fromVersion="1.0.0" toVersion="2.0.0" changes={changes} appName="App" />,
    );
    expect(container.textContent).toContain("1.0.0 → 2.0.0");
  });

  it("shows change summary counts", () => {
    const { container } = render(
      <VersionDiffCard fromVersion="1.0" toVersion="2.0" changes={changes} appName="App" />,
    );
    expect(container.textContent).toContain("+1 added");
    expect(container.textContent).toContain("−1 removed");
    expect(container.textContent).toContain("~1 modified");
  });

  it("renders field paths", () => {
    const { container } = render(
      <VersionDiffCard fromVersion="1.0" toVersion="2.0" changes={changes} appName="App" />,
    );
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("config.debug");
    expect(container.textContent).toContain("config.cache_ttl");
  });

  it("shows old → new for modified", () => {
    const { container } = render(
      <VersionDiffCard fromVersion="1.0" toVersion="2.0" changes={changes} appName="App" />,
    );
    expect(container.textContent).toContain('"App v1"');
    expect(container.textContent).toContain('"App v2"');
  });

  it("shows no changes message", () => {
    const { container } = render(
      <VersionDiffCard fromVersion="1.0" toVersion="1.0" changes={[]} appName="App" />,
    );
    expect(container.textContent).toContain("No changes");
  });
});
