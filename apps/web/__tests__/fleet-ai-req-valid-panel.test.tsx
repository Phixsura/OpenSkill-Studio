import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiReqValidPanel } from "@/components/fleet-ai-req-valid-panel";
describe("FleetAiReqValidPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiReqValidPanel validators={5} active={5} validated={500000000} rejected={200000} schemas={500} />);
    expect(container.textContent).toContain("Request Validator");
}); });
