import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiOnboardingChecklistCard from "../src/components/api-developer-api-api-onboarding-checklist-card";

const items = [
  { item_id: "key", title: "Create API Key", completed: true, required: true },
  { item_id: "call", title: "First API Call", completed: false, required: true },
  { item_id: "hook", title: "Set Up Webhook", completed: false, required: false },
];

describe("APIDeveloperAPIApiOnboardingChecklistCard", () => {
  it("shows checklist", () => {
    const { container } = render(<APIDeveloperAPIApiOnboardingChecklistCard items={items} completionPct={33.3} allRequiredDone={false} developerName="dev1" appName="App" />);
    expect(container.textContent).toContain("Onboarding Checklist");
    expect(container.textContent).toContain("33.3%");
    expect(container.textContent).toContain("Create API Key");
    expect(container.textContent).toContain("First API Call");
    expect(container.textContent).toContain("(optional)");
  });
});
