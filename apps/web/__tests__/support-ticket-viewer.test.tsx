import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SupportTicketViewer } from "@/components/support-ticket-viewer";

const mockTicket = {
  id: "t1", subject: "App crashes on load", status: "in_progress" as const,
  priority: "high" as const, reporter: "alice", assignee: "bob",
  category: "bug", createdAt: "Oct 25, 2026",
  messages: [
    { authorId: "alice", authorName: "Alice", body: "App crashes when I open settings", timestamp: "10:00", isInternal: false },
    { authorId: "bob", authorName: "Bob (Dev)", body: "Can you share your browser version?", timestamp: "10:15", isInternal: false },
  ],
};

describe("SupportTicketViewer", () => {
  it("renders ticket details", () => {
    const { container } = render(<SupportTicketViewer ticket={mockTicket} currentUserId="bob" />);
    expect(container.textContent).toContain("App crashes on load");
    expect(container.textContent).toContain("HIGH");
    expect(container.textContent).toContain("in progress");
    expect(container.textContent).toContain("alice");
  });

  it("renders messages", () => {
    const { container } = render(<SupportTicketViewer ticket={mockTicket} currentUserId="bob" />);
    expect(container.textContent).toContain("crashes when I open settings");
    expect(container.textContent).toContain("browser version");
  });

  it("calls onReply", () => {
    const onReply = vi.fn();
    const { getByText, getByPlaceholderText } = render(
      <SupportTicketViewer ticket={mockTicket} currentUserId="bob" onReply={onReply} />
    );
    fireEvent.change(getByPlaceholderText("Type your reply..."), { target: { value: "Try clearing cache" } });
    fireEvent.click(getByText("Reply"));
    expect(onReply).toHaveBeenCalledWith("Try clearing cache");
  });
});
