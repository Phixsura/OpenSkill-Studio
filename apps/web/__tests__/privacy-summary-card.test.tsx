import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PrivacySummaryCard } from "@/components/privacy-summary-card";

describe("PrivacySummaryCard", () => {
  it("renders privacy", () => {
    const { container } = render(
      <PrivacySummaryCard appName="My App" maxRisk="high" hasPrivacyPolicy={true}
        privacyUrl="https://example.com/privacy"
        dataCollected={[
          { id: "personal", icon: "👤", label: "Personal Info", risk: "high" },
          { id: "usage", icon: "📊", label: "Usage", risk: "medium" },
        ]} />
    );
    expect(container.textContent).toContain("Data Privacy");
    expect(container.textContent).toContain("high risk");
    expect(container.textContent).toContain("Personal Info");
    expect(container.textContent).toContain("View Privacy Policy");
  });
});
