import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AuditTrailViewer } from "@/components/audit-trail-viewer";

const mockEvents = [
  { id: "1", action: "extension.published", actor: "alice", actorType: "user" as const,
    target: "slack-bot", targetType: "extension", timestamp: "2m ago", details: { version: "2.0.0" } },
  { id: "2", action: "permission.granted", actor: "system", actorType: "system" as const,
    target: "ext-abc", targetType: "extension", timestamp: "5m ago", details: { scope: "read" } },
  { id: "3", action: "key.revoked", actor: "bob", actorType: "user" as const,
    target: "key-xyz", targetType: "api_key", timestamp: "1h ago", details: {} },
];

describe("AuditTrailViewer", () => {
  it("renders events with actors and actions", () => {
    const { container } = render(<AuditTrailViewer events={mockEvents} />);
    expect(container.textContent).toContain("Audit Trail");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("extension.published");
    expect(container.textContent).toContain("slack-bot");
    expect(container.textContent).toContain("3 events");
  });

  it("shows event details", () => {
    const { container } = render(<AuditTrailViewer events={mockEvents} />);
    expect(container.textContent).toContain("version: 2.0.0");
    expect(container.textContent).toContain("scope: read");
  });

  it("filters by action", () => {
    const { container, getByRole } = render(<AuditTrailViewer events={mockEvents} />);
    fireEvent.change(getByRole("combobox"), { target: { value: "key.revoked" } });
    expect(container.textContent).toContain("1 events");
    expect(container.textContent).toContain("bob");
  });

  it("shows load more button", () => {
    const onLoad = vi.fn();
    const { getByText } = render(
      <AuditTrailViewer events={mockEvents} hasMore={true} onLoadMore={onLoad} />
    );
    fireEvent.click(getByText("Load more events..."));
    expect(onLoad).toHaveBeenCalled();
  });
});
