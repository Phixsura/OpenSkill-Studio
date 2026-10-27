import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiChangelogViewer } from "@/components/api-changelog-viewer";

const MOCK_CHANGELOG = {
  from_version: "1.0",
  to_version: "2.0",
  generated_at: "2026-10-28T10:00:00Z",
  summary: { breaking: 2, non_breaking: 1, patch: 1, has_breaking: true },
  changes: [
    {
      method: "GET",
      path: "/api/v1/skills/search",
      change_type: "added" as const,
      severity: "non_breaking" as const,
      summary: "New endpoint: GET /api/v1/skills/search",
      param_changes: [
        { name: "q", change_type: "added" as const, old_type: null, new_type: "string" },
      ],
      response_changes: [],
      migration_hint: null,
    },
    {
      method: "DELETE",
      path: "/api/v1/skills/{id}",
      change_type: "removed" as const,
      severity: "breaking" as const,
      summary: "Removed endpoint: DELETE /api/v1/skills/{id}",
      param_changes: [],
      response_changes: [],
      migration_hint: "Clients using DELETE /api/v1/skills/{id} must remove these calls.",
    },
    {
      method: "POST",
      path: "/api/v1/skills",
      change_type: "modified" as const,
      severity: "breaking" as const,
      summary: "Modified: 1 param change(s)",
      param_changes: [
        {
          name: "level",
          change_type: "modified" as const,
          old_type: "string",
          new_type: "integer",
        },
      ],
      response_changes: [
        { name: "category", change_type: "added" as const, old_type: null, new_type: "string" },
      ],
      migration_hint: null,
    },
    {
      method: "GET",
      path: "/api/v1/skills/{id}",
      change_type: "deprecated" as const,
      severity: "non_breaking" as const,
      summary: "Deprecated: GET /api/v1/skills/{id}",
      param_changes: [],
      response_changes: [],
      migration_hint: "This endpoint will be removed in a future version.",
    },
  ],
};

const CLEAN_CHANGELOG = {
  from_version: "1.0",
  to_version: "1.1",
  generated_at: "2026-10-28T10:00:00Z",
  summary: { breaking: 0, non_breaking: 1, patch: 0, has_breaking: false },
  changes: [
    {
      method: "GET",
      path: "/api/v1/packs",
      change_type: "added" as const,
      severity: "non_breaking" as const,
      summary: "New endpoint",
      param_changes: [],
      response_changes: [],
      migration_hint: null,
    },
  ],
};

describe("ApiChangelogViewer", () => {
  it("renders version transition header", () => {
    const { container } = render(<ApiChangelogViewer changelog={MOCK_CHANGELOG} />);
    expect(container.textContent).toContain("1.0 → 2.0");
  });

  it("renders summary counts", () => {
    const { container } = render(<ApiChangelogViewer changelog={MOCK_CHANGELOG} />);
    expect(container.textContent).toContain("2 breaking");
    expect(container.textContent).toContain("1 non-breaking");
  });

  it("shows breaking warning banner", () => {
    const { container } = render(<ApiChangelogViewer changelog={MOCK_CHANGELOG} />);
    expect(container.textContent).toContain("breaking changes");
    expect(container.textContent).toContain("migration hints");
  });

  it("hides breaking warning when no breaking changes", () => {
    const { container } = render(<ApiChangelogViewer changelog={CLEAN_CHANGELOG} />);
    expect(container.textContent).not.toContain("breaking changes");
  });

  it("renders HTTP method badges", () => {
    const { container } = render(<ApiChangelogViewer changelog={MOCK_CHANGELOG} />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("DELETE");
    expect(container.textContent).toContain("POST");
  });

  it("renders endpoint paths", () => {
    const { container } = render(<ApiChangelogViewer changelog={MOCK_CHANGELOG} />);
    expect(container.textContent).toContain("/api/v1/skills/search");
    expect(container.textContent).toContain("/api/v1/skills/{id}");
  });

  it("renders change type icons", () => {
    const { container } = render(<ApiChangelogViewer changelog={MOCK_CHANGELOG} />);
    expect(container.textContent).toContain("+"); // added
    expect(container.textContent).toContain("−"); // removed
    expect(container.textContent).toContain("~"); // modified
    expect(container.textContent).toContain("⚠"); // deprecated
  });

  it("expands to show migration hint", () => {
    const { container } = render(<ApiChangelogViewer changelog={MOCK_CHANGELOG} />);
    const buttons = container.querySelectorAll("button[aria-expanded]");
    // Find the DELETE row (has migration hint)
    const deleteBtn = Array.from(buttons).find((b) => b.textContent?.includes("DELETE"));
    expect(deleteBtn).toBeTruthy();
    fireEvent.click(deleteBtn!);
    expect(container.textContent).toContain("Migration:");
    expect(container.textContent).toContain("must remove these calls");
  });

  it("expands to show param changes", () => {
    const { container } = render(<ApiChangelogViewer changelog={MOCK_CHANGELOG} />);
    const buttons = container.querySelectorAll("button[aria-expanded]");
    const postBtn = Array.from(buttons).find((b) => b.textContent?.includes("POST"));
    fireEvent.click(postBtn!);
    expect(container.textContent).toContain("Parameters");
    expect(container.textContent).toContain("level");
    expect(container.textContent).toContain("string → integer");
  });

  it("expands to show response changes", () => {
    const { container } = render(<ApiChangelogViewer changelog={MOCK_CHANGELOG} />);
    const buttons = container.querySelectorAll("button[aria-expanded]");
    const postBtn = Array.from(buttons).find((b) => b.textContent?.includes("POST"));
    fireEvent.click(postBtn!);
    expect(container.textContent).toContain("Response");
    expect(container.textContent).toContain("category");
  });

  it("shows empty state when no changes", () => {
    const empty = {
      ...CLEAN_CHANGELOG,
      changes: [],
      summary: { breaking: 0, non_breaking: 0, patch: 0, has_breaking: false },
    };
    const { container } = render(<ApiChangelogViewer changelog={empty} />);
    expect(container.textContent).toContain("No changes detected");
  });
});
