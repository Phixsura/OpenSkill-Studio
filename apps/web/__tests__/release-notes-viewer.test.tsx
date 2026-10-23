import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseNotesViewer } from "@/components/release-notes-viewer";

describe("ReleaseNotesViewer", () => {
  it("renders notes", () => {
    const { container } = render(
      <ReleaseNotesViewer version="3.0.0" prCount={3} contributorCount={2}
        contributors={["alice", "bob"]}
        sections={{ feature: ["Dark mode (@alice)"], bugfix: ["Login fix (@bob)", "CSS fix (@alice)"] }} />
    );
    expect(container.textContent).toContain("Release v3.0.0");
    expect(container.textContent).toContain("3 PRs");
    expect(container.textContent).toContain("2 contributors");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("Login fix");
    expect(container.textContent).toContain("alice, bob");
  });
});
