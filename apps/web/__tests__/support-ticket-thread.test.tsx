import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SupportTicketThread } from "@/components/support-ticket-thread";

const ticket = {
  ticketId: "tkt-1", subject: "Bug Report", priority: "high", status: "in_progress", userId: "u1",
  messages: [
    { senderId: "u1", content: "Found a bug", sentAt: Date.now() },
    { senderId: "dev-1", content: "Looking into it", sentAt: Date.now() },
  ],
};

describe("SupportTicketThread", () => {
  it("renders thread", () => {
    const { container } = render(<SupportTicketThread ticket={ticket} currentUserId="u1" />);
    expect(container.textContent).toContain("Bug Report");
    expect(container.textContent).toContain("Found a bug");
    expect(container.textContent).toContain("Looking into it");
  });
  it("send reply", () => {
    const fn = vi.fn();
    const { container } = render(<SupportTicketThread ticket={ticket} currentUserId="u1" onReply={fn} />);
    const input = container.querySelector("input")!;
    fireEvent.change(input, { target: { value: "Thanks!" } });
    fireEvent.click(container.querySelector("button:last-of-type")!);
    expect(fn).toHaveBeenCalledWith("Thanks!");
  });
});
