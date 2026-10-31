import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppChangelog } from "@/components/app-changelog";

const ENTRIES = [
  { version: "2.0.0", notes: "Big update", breaking: false,
    changes: [{ type: "permissions_added", items: ["write:cohorts"] }, { type: "events_added", items: ["cohort.member_added"] }] },
  { version: "1.0.0", notes: "Initial release", breaking: false, changes: [] },
];

describe("AppChangelog", () => {
  it("renders entries", () => {
    const { container } = render(<AppChangelog entries={ENTRIES} />);
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("1.0.0");
  });

  it("shows notes", () => {
    const { container } = render(<AppChangelog entries={ENTRIES} />);
    expect(container.textContent).toContain("Big update");
  });

  it("shows changes", () => {
    const { container } = render(<AppChangelog entries={ENTRIES} />);
    expect(container.textContent).toContain("write:cohorts");
  });

  it("shows empty state", () => {
    const { container } = render(<AppChangelog entries={[]} />);
    expect(container.textContent).toContain("No changelog");
  });

  it("shows breaking badge", () => {
    const breaking = [{ version: "3.0.0", notes: "", breaking: true, changes: [{ type: "permissions_removed", items: ["read:x"], breaking: true }] }];
    const { container } = render(<AppChangelog entries={breaking} />);
    expect(container.textContent).toContain("Breaking");
  });
});
