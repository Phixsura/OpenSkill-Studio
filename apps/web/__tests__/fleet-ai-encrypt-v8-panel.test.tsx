import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEncryptV8Panel } from "@/components/fleet-ai-encrypt-v8-panel";
describe("FleetAiEncryptV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiEncryptV8Panel systems={5} active={5} dataEb={500} keys={5000000} e2e={true} quantum={true} />);
    expect(container.textContent).toContain("Encryption v8");
}); });
