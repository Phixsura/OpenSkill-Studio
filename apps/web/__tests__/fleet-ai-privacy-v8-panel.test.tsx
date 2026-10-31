import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPrivacyV8Panel } from "@/components/fleet-ai-privacy-v8-panel";
describe("FleetAiPrivacyV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPrivacyV8Panel systems={3} active={3} pii={5000000} redacted={5000000} gdpr={true} ccpa={true} />);
    expect(container.textContent).toContain("Privacy v8");
}); });
