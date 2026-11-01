import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IncidentManagerCard from "../src/components/api-developer-platform-sdk-consumer-api-incident-manager-card";

describe("IncidentManagerCard", () => {
  it("renders title and incidents", () => {
    const { container } = render(<IncidentManagerCard />);
    expect(container.textContent).toContain("Incident Manager");
    expect(container.textContent).toContain("Payment API Timeout");
    expect(container.textContent).toContain("Elevated Error Rate");
  });

  it("shows severity and active count", () => {
    const { container } = render(<IncidentManagerCard />);
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("investigating");
    expect(container.textContent).toContain("2 active incidents");
  });
});
