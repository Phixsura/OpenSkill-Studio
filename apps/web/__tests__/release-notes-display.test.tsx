import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseNotesDisplay } from "@/components/release-notes-display";

describe("ReleaseNotesDisplay", () => {
  it("renders notes", () => {
    const { container } = render(
      <ReleaseNotesDisplay version="3.5.0" date="2026-10-24" totalPrs={3}
        hasBreaking={false} contributors={["alice", "bob"]}
        sections={[
          { type: "added", count: 2, items: [
            { title: "SSO support", number: 100, author: "alice" },
            { title: "Dark mode", number: 102, author: "alice" },
          ]},
          { type: "fixed", count: 1, items: [
            { title: "Login bug", number: 101, author: "bob" },
          ]},
        ]} />
    );
    expect(container.textContent).toContain("v3.5.0");
    expect(container.textContent).toContain("3 changes");
    expect(container.textContent).toContain("2 contributors");
    expect(container.textContent).toContain("SSO support");
    expect(container.textContent).toContain("#100");
    expect(container.textContent).toContain("alice, bob");
  });
});
