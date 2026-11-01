import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangeRequestCard from "../src/components/api-change-request-card";

const requests = [
  { request_id: "cr1", title: "Add email field", impact: "minor", status: "pending" as const, submitter: "alice" },
  { request_id: "cr2", title: "Remove v1 API", impact: "breaking", status: "approved" as const, submitter: "bob" },
];

describe("APIChangeRequestCard", () => {
  it("renders header and pending count", () => {
    const { container } = render(<APIChangeRequestCard requests={requests} appName="App" />);
    expect(container.textContent).toContain("Change Requests");
    expect(container.textContent).toContain("1 pending");
  });

  it("shows status and impact", () => {
    const { container } = render(<APIChangeRequestCard requests={requests} appName="App" />);
    expect(container.textContent).toContain("pending");
    expect(container.textContent).toContain("Add email field");
    expect(container.textContent).toContain("breaking");
  });

  it("shows empty state", () => {
    const { container } = render(<APIChangeRequestCard requests={[]} appName="App" />);
    expect(container.textContent).toContain("No change requests");
  });
});
