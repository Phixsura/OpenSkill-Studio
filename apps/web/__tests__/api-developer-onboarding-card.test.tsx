import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperOnboardingCard from "../src/components/api-developer-onboarding-card";

const devs = [
  { developer_id: "alice", completion_pct: 100, completed_count: 3, total_steps: 3, is_complete: true },
  { developer_id: "bob", completion_pct: 33.3, completed_count: 1, total_steps: 3, is_complete: false },
];

describe("APIDeveloperOnboardingCard", () => {
  it("renders header and completion rate", () => {
    const { container } = render(<APIDeveloperOnboardingCard developers={devs} completionRate={50} steps={["s1", "s2", "s3"]} appName="App" />);
    expect(container.textContent).toContain("Dev Onboarding");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("3 steps");
  });

  it("shows developer progress", () => {
    const { container } = render(<APIDeveloperOnboardingCard developers={devs} completionRate={50} steps={["s1", "s2", "s3"]} appName="App" />);
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("3/3");
    expect(container.textContent).toContain("bob");
    expect(container.textContent).toContain("1/3");
  });

  it("shows empty state", () => {
    const { container } = render(<APIDeveloperOnboardingCard developers={[]} completionRate={0} steps={[]} appName="App" />);
    expect(container.textContent).toContain("No developers onboarding");
  });
});
