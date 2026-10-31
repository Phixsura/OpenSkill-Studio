import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPrivacyV7Panel } from "@/components/fleet-ai-privacy-v7-panel";
describe("FleetAiPrivacyV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPrivacyV7Panel systems={3} active={3} pii={200000} redacted={200000} gdpr={true} />);
    expect(container.textContent).toContain("Privacy v7");
}); });
