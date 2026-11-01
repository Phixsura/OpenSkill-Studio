import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseNotesPanel } from "@/components/release-notes-panel";

const mockNote = {
  version: "2.0.0", title: "Major Update", summary: "Big changes ahead",
  features: ["Dark mode", "Export CSV"], fixes: ["Login bug"],
  breaking: ["New API format"], highlights: ["Complete redesign"],
  contributors: ["alice", "bob"],
};

describe("ReleaseNotesPanel", () => {
  it("renders release note", () => {
    const { container } = render(<ReleaseNotesPanel note={mockNote} />);
    expect(container.textContent).toContain("Major Update");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("Login bug");
    expect(container.textContent).toContain("New API format");
    expect(container.textContent).toContain("Complete redesign");
    expect(container.textContent).toContain("alice");
  });
});
