import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentPage } from "@/components/incident-page";

describe("IncidentPage", () => {
  const timeline = [{ status: "investigating", icon: "🔍", message: "Looking into it", timestamp: "2026-10-24T10:05:00Z" }];
  it("renders incident", () => {
    const { container } = render(
      <IncidentPage title="API Latency" severity="major" status="identified"
        statusIcon="🎯" affectedServices={["API"]} timeline={timeline}
        isResolved={false} createdAt="2026-10-24" />
    );
    expect(container.textContent).toContain("API Latency");
    expect(container.textContent).toContain("major");
    expect(container.textContent).toContain("Looking into it");
    expect(container.textContent).toContain("API");
  });
});
