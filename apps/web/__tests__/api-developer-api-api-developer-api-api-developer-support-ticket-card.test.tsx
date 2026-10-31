import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperSupportTicketCard from "../src/components/api-developer-api-api-developer-api-api-developer-support-ticket-card";

const tickets = [
  { ticket_id: "t1", developer_id: "d1", subject: "Auth broken", priority: "urgent", status: "open" },
  { ticket_id: "t2", developer_id: "d2", subject: "Docs unclear", priority: "low", status: "resolved" },
];

describe("Card", () => {
  it("shows tickets", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperSupportTicketCard tickets={tickets} openCount={1} avgResolutionHours={4.5} appName="App" />);
    expect(container.textContent).toContain("Support Tickets");
    expect(container.textContent).toContain("1 open");
    expect(container.textContent).toContain("Auth broken");
    expect(container.textContent).toContain("urgent");
    expect(container.textContent).toContain("4.5h");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperSupportTicketCard tickets={[]} openCount={0} avgResolutionHours={0} appName="App" />);
    expect(container.textContent).toContain("No tickets");
  });
});
