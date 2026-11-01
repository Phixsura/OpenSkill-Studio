import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RunbookCard from "../src/components/api-developer-platform-sdk-consumer-api-runbook-card";

describe("RunbookCard", () => {
  it("renders title and runbooks", () => {
    const { container } = render(<RunbookCard />);
    expect(container.textContent).toContain("API Runbooks");
    expect(container.textContent).toContain("Incident Response");
    expect(container.textContent).toContain("Database Failover");
  });

  it("shows triggers and count", () => {
    const { container } = render(<RunbookCard />);
    expect(container.textContent).toContain("incident");
    expect(container.textContent).toContain("manual");
    expect(container.textContent).toContain("3 runbooks");
  });
});
