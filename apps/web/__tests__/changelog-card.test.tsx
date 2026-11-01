import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogCard from "../src/components/changelog-card";

const release1 = {
  version: "2.0.0",
  date: "2026-10-28",
  summary: "Major release with breaking changes",
  entries: [
    { description: "New dashboard API", category: "added" as const, breaking: false },
    { description: "Removed legacy v1 endpoints", category: "removed" as const, breaking: true },
    { description: "Auth token format changed", category: "security" as const, breaking: false },
  ],
};

const release2 = {
  version: "1.1.0",
  date: "2026-09-15",
  summary: "",
  entries: [
    { description: "Fixed pagination bug", category: "fixed" as const, breaking: false },
    {
      description: "Deprecated old webhook format",
      category: "deprecated" as const,
      breaking: false,
    },
  ],
};

describe("ChangelogCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ChangelogCard releases={[release1]} appName="My App" />);
    expect(container.textContent).toContain("Changelog");
    expect(container.textContent).toContain("My App");
  });

  it("shows release and change counts", () => {
    const { container } = render(<ChangelogCard releases={[release1, release2]} appName="App" />);
    expect(container.textContent).toContain("2 releases");
    expect(container.textContent).toContain("5 changes");
  });

  it("renders version and date", () => {
    const { container } = render(<ChangelogCard releases={[release1]} appName="App" />);
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("2026-10-28");
  });

  it("shows release summary", () => {
    const { container } = render(<ChangelogCard releases={[release1]} appName="App" />);
    expect(container.textContent).toContain("Major release with breaking changes");
  });

  it("renders category badges", () => {
    const { container } = render(<ChangelogCard releases={[release1, release2]} appName="App" />);
    expect(container.textContent).toContain("Added");
    expect(container.textContent).toContain("Removed");
    expect(container.textContent).toContain("Security");
    expect(container.textContent).toContain("Fixed");
    expect(container.textContent).toContain("Deprecated");
  });

  it("shows entry descriptions", () => {
    const { container } = render(<ChangelogCard releases={[release1]} appName="App" />);
    expect(container.textContent).toContain("New dashboard API");
    expect(container.textContent).toContain("Removed legacy v1 endpoints");
  });

  it("flags breaking changes", () => {
    const { container } = render(<ChangelogCard releases={[release1]} appName="App" />);
    expect(container.textContent).toContain("BREAKING");
    expect(container.textContent).toContain("⚠");
  });

  it("shows empty state", () => {
    const { container } = render(<ChangelogCard releases={[]} appName="App" />);
    expect(container.textContent).toContain("No releases yet");
  });

  it("renders singular counts correctly", () => {
    const single = {
      version: "1.0.0",
      date: "2026-01-01",
      summary: "",
      entries: [{ description: "Init", category: "added" as const, breaking: false }],
    };
    const { container } = render(<ChangelogCard releases={[single]} appName="App" />);
    expect(container.textContent).toContain("1 release");
    expect(container.textContent).toContain("1 change");
    expect(container.textContent).not.toContain("1 releases");
  });
});
