import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-onboarding-checklist-card";

describe("ConsumerApiOnboardingChecklistCard", () => {
  it("shows checklist", () => {
    const items = [{ id: "i1", title: "Create API Key", completed: true, required: true }, { id: "i2", title: "Set Webhook", completed: false, required: true }];
    const { container } = render(<Card items={items} progressPct={50} fullyOnboarded={false} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Onboarding");
    expect(container.textContent).toContain("Create API Key");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("✅");
  });
  it("shows completed", () => {
    const items = [{ id: "i1", title: "Done", completed: true, required: true }];
    const { container } = render(<Card items={items} progressPct={100} fullyOnboarded={true} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("100%");
  });
});
