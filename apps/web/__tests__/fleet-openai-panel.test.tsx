import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOpenaiPanel } from "@/components/fleet-openai-panel";
describe("FleetOpenaiPanel", () => { it("renders", () => {
    const { container } = render(<FleetOpenaiPanel orgs={3} active={3} requests={10000000} cost={15000} />);
    expect(container.textContent).toContain("OpenAI");
}); });
