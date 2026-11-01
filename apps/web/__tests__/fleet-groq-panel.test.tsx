import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGroqPanel } from "@/components/fleet-groq-panel";
describe("FleetGroqPanel", () => { it("renders", () => {
    const { container } = render(<FleetGroqPanel endpoints={5} active={5} tokensPerSec={5000} requests={25000000} />);
    expect(container.textContent).toContain("Groq");
}); });
