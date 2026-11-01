import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIReleaseNoteCard from "../src/components/api-release-note-card";

const notes = [
  { note_id: "n1", version: "v2.0", title: "Major Release", highlights: ["Dark mode", "New API"], known_issues: ["Login bug"], published: true },
  { note_id: "n2", version: "v2.1", title: "Patch", highlights: ["Bug fix"], known_issues: [], published: false },
];

describe("APIReleaseNoteCard", () => {
  it("renders header and published count", () => {
    const { container } = render(<APIReleaseNoteCard notes={notes} appName="App" />);
    expect(container.textContent).toContain("Release Notes");
    expect(container.textContent).toContain("1/2 published");
  });

  it("shows titles and versions", () => {
    const { container } = render(<APIReleaseNoteCard notes={notes} appName="App" />);
    expect(container.textContent).toContain("Major Release");
    expect(container.textContent).toContain("v2.0");
  });

  it("shows highlights and issues count", () => {
    const { container } = render(<APIReleaseNoteCard notes={notes} appName="App" />);
    expect(container.textContent).toContain("2 highlights");
    expect(container.textContent).toContain("1 known issues");
  });

  it("shows empty state", () => {
    const { container } = render(<APIReleaseNoteCard notes={[]} appName="App" />);
    expect(container.textContent).toContain("No release notes");
  });
});
