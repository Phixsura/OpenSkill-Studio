import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiChangelogPage } from "@/components/api-changelog-page";

describe("ApiChangelogPage", () => {
  const versions = [{ version: "2026-10-01", title: "October 2026", changeCount: 3 }];
  const changes = [
    { type: "added", endpoint: "POST /api/v1/apps/{id}/publish", description: "Publish app" },
  ];
  it("renders changelog", () => {
    const { container } = render(
      <ApiChangelogPage versions={versions} selectedChanges={changes}
        selectedVersion="2026-10-01" hasBreaking={false} onSelectVersion={vi.fn()} />
    );
    expect(container.textContent).toContain("API Changelog");
    expect(container.textContent).toContain("October 2026");
    expect(container.textContent).toContain("Publish app");
  });
});
