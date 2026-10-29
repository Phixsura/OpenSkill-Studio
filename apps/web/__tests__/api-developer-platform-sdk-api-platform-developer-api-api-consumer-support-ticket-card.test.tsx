import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-support-ticket-card";

describe("SupportTicketCard", () => {
  it("shows tickets", () => {
    const tickets = [{ ticket_id: "t1", consumer_id: "c1", subject: "Auth issue", priority: "urgent", status: "open" }];
    const { container } = render(<Card tickets={tickets} openCount={1} urgentCount={1} appName="App" />);
    expect(container.textContent).toContain("Support Tickets");
    expect(container.textContent).toContain("1 urgent");
    expect(container.textContent).toContain("Auth issue");
  });
  it("shows empty", () => {
    const { container } = render(<Card tickets={[]} openCount={0} urgentCount={0} appName="App" />);
    expect(container.textContent).toContain("No tickets");
  });
});
