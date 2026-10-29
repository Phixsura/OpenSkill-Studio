import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiPlatformIncidentResponseCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-platform-incident-response-card";

const incidents = [{ incident_id: "i1", title: "Database Outage", severity: "sev1", status: "mitigating", commander: "alice", duration_minutes: 45, affected_services: ["db", "api"] }];

describe("Card", () => {
  it("shows incidents", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformIncidentResponseCard incidents={incidents} activeCount={1} mttrMinutes={30} appName="App" />);
    expect(container.textContent).toContain("Incident Response");
    expect(container.textContent).toContain("MTTR: 30m");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("Database Outage");
    expect(container.textContent).toContain("sev1");
    expect(container.textContent).toContain("IC: alice");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformIncidentResponseCard incidents={[]} activeCount={0} mttrMinutes={0} appName="App" />);
    expect(container.textContent).toContain("No incidents");
  });
});
