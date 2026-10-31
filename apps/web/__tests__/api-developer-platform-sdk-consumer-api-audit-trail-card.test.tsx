import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AuditTrailCard from "../src/components/api-developer-platform-sdk-consumer-api-audit-trail-card";

describe("AuditTrailCard", () => {
  it("renders title and entries", () => {
    const { container } = render(<AuditTrailCard />);
    expect(container.textContent).toContain("Audit Trail");
    expect(container.textContent).toContain("api_key:k-1234");
    expect(container.textContent).toContain("alice");
  });

  it("shows integrity status", () => {
    const { container } = render(<AuditTrailCard />);
    expect(container.textContent).toContain("Chain Valid");
    expect(container.textContent).toContain("156 entries verified");
  });
});
