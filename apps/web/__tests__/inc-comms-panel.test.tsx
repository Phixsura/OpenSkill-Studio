import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncCommsPanel } from "@/components/inc-comms-panel";

describe("IncCommsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <IncCommsPanel total={2} messages={[
        { type: "investigating", message: "We are investigating API issues.", channels: ["email", "slack"] },
        { type: "resolved", message: "Issue resolved.", channels: ["email", "status_page"] },
      ]} />
    );
    expect(container.textContent).toContain("Incident Comms");
    expect(container.textContent).toContain("2 messages");
    expect(container.textContent).toContain("investigating");
    expect(container.textContent).toContain("We are investigating");
    expect(container.textContent).toContain("resolved");
    expect(container.textContent).toContain("email, slack");
  });
});
