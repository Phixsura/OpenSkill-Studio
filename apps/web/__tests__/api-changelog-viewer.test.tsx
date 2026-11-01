import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiChangelogViewer } from "@/components/api-changelog-viewer";

const changelog = {
  fromVersion: "1.0", toVersion: "2.0",
  changes: [
    { changeType: "added", path: "/users", method: "POST", description: "Create user", breaking: false },
    { changeType: "removed", path: "/legacy", method: "GET", description: "Removed", breaking: true },
  ],
};

describe("ApiChangelogViewer", () => {
  it("renders changes", () => {
    const { container } = render(<ApiChangelogViewer changelog={changelog} />);
    expect(container.textContent).toContain("1.0 → 2.0");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("/users");
  });
  it("shows empty state", () => {
    const { container } = render(<ApiChangelogViewer changelog={{ fromVersion: "1.0", toVersion: "1.0", changes: [] }} />);
    expect(container.textContent).toContain("No API changes");
  });
});
