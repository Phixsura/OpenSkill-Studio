import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIIncidentResponseCard from "../src/components/api-developer-api-incident-response-card";

const responses = [
  { response_id: "r1", incident_type: "API Outage", status: "mitigating", current_step: 1, total_steps: 3, responder_count: 2 },
];

describe("APIDeveloperAPIIncidentResponseCard", () => {
  it("shows responses", () => {
    const { container } = render(<APIDeveloperAPIIncidentResponseCard responses={responses} appName="App" />);
    expect(container.textContent).toContain("Incident Response");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("mitigating");
    expect(container.textContent).toContain("API Outage");
    expect(container.textContent).toContain("step 2/3");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIIncidentResponseCard responses={[]} appName="App" />);
    expect(container.textContent).toContain("No incident responses");
  });
});
