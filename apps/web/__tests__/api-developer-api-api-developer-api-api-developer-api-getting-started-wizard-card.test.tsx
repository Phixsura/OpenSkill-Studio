import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiGettingStartedWizardCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-getting-started-wizard-card";

const progress = { developer_id: "dev1", completed_steps: ["create_account", "generate_api_key"], current_step: "make_first_call", progress_pct: 40, is_complete: false };

describe("Card", () => {
  it("shows wizard", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiGettingStartedWizardCard progress={progress} completionRate={35} appName="App" />);
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("40%");
    expect(container.textContent).toContain("Create Account");
    expect(container.textContent).toContain("First Call");
    expect(container.textContent).toContain("35% of developers completed");
  });
});
