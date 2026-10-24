import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTwilioPanel } from "@/components/fleet-twilio-panel";
describe("FleetTwilioPanel", () => { it("renders", () => {
    const { container } = render(<FleetTwilioPanel accounts={3} active={3} messages={500000} calls={20000} />);
    expect(container.textContent).toContain("Twilio");
    expect(container.textContent).toContain("500,000");
}); });
