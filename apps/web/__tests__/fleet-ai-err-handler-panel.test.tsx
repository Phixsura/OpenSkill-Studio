import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiErrHandlerPanel } from "@/components/fleet-ai-err-handler-panel";
describe("FleetAiErrHandlerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiErrHandlerPanel handlers={4} active={4} errors={2000} recovered={1900} escalated={100} recoveryRate={95} />);
    expect(container.textContent).toContain("Error Handler");
}); });
