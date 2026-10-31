import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSecPosturePanel } from "@/components/fleet-ai-sec-posture-panel";
describe("FleetAiSecPosturePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSecPosturePanel assessors={3} active={3} score={98} vulns={0} controls={500} compliance={100} />);
    expect(container.textContent).toContain("Security Posture");
}); });
