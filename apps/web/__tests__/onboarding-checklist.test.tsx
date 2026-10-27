import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingChecklist } from "@/components/onboarding-checklist";

const MOCK_STEPS = [
  {
    step_id: "manifest",
    title: "Complete Manifest",
    description: "Fill in app details",
    required: true,
    status: "completed" as const,
  },
  {
    step_id: "permissions",
    title: "Declare Permissions",
    description: "Set API scopes",
    required: true,
    status: "pending" as const,
  },
  {
    step_id: "webhook",
    title: "Set Up Webhooks",
    description: "Configure endpoint",
    required: false,
    status: "pending" as const,
  },
  {
    step_id: "screenshots",
    title: "Add Screenshots",
    description: "Upload images",
    required: true,
    status: "pending" as const,
  },
];

const defaultProps = {
  appName: "My App",
  steps: MOCK_STEPS,
  progress: { total_steps: 4, completed: 1, progress_pct: 25.0, can_publish: false },
  onComplete: vi.fn(),
  onSkip: vi.fn(),
};

describe("OnboardingChecklist", () => {
  it("renders heading and app name", () => {
    const { container } = render(<OnboardingChecklist {...defaultProps} />);
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("My App");
  });

  it("renders progress percentage", () => {
    const { container } = render(<OnboardingChecklist {...defaultProps} />);
    expect(container.textContent).toContain("25%");
  });

  it("renders step titles", () => {
    const { container } = render(<OnboardingChecklist {...defaultProps} />);
    expect(container.textContent).toContain("Complete Manifest");
    expect(container.textContent).toContain("Declare Permissions");
    expect(container.textContent).toContain("Set Up Webhooks");
  });

  it("renders step descriptions", () => {
    const { container } = render(<OnboardingChecklist {...defaultProps} />);
    expect(container.textContent).toContain("Fill in app details");
  });

  it("shows required label", () => {
    const { container } = render(<OnboardingChecklist {...defaultProps} />);
    expect(container.textContent).toContain("required");
  });

  it("shows checkmark for completed steps", () => {
    const { container } = render(<OnboardingChecklist {...defaultProps} />);
    expect(container.textContent).toContain("✓");
  });

  it("shows Complete button for pending steps", () => {
    const { container } = render(<OnboardingChecklist {...defaultProps} />);
    const completeBtns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Complete",
    );
    expect(completeBtns.length).toBe(3); // 3 pending steps
  });

  it("calls onComplete when Complete clicked", () => {
    const onComplete = vi.fn();
    const { container } = render(<OnboardingChecklist {...defaultProps} onComplete={onComplete} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Complete",
    );
    fireEvent.click(btn!);
    expect(onComplete).toHaveBeenCalledWith("permissions");
  });

  it("shows Skip for optional pending steps only", () => {
    const { container } = render(<OnboardingChecklist {...defaultProps} />);
    const skipBtns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Skip",
    );
    expect(skipBtns.length).toBe(1); // only webhook is optional+pending
  });

  it("calls onSkip when Skip clicked", () => {
    const onSkip = vi.fn();
    const { container } = render(<OnboardingChecklist {...defaultProps} onSkip={onSkip} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Skip",
    );
    fireEvent.click(btn!);
    expect(onSkip).toHaveBeenCalledWith("webhook");
  });

  it("shows Ready to publish when can_publish", () => {
    const canPublish = { ...defaultProps.progress, can_publish: true, progress_pct: 100 };
    const { container } = render(<OnboardingChecklist {...defaultProps} progress={canPublish} />);
    expect(container.textContent).toContain("Ready to publish");
  });

  it("hides Ready to publish when not ready", () => {
    const { container } = render(<OnboardingChecklist {...defaultProps} />);
    expect(container.textContent).not.toContain("Ready to publish");
  });
});
