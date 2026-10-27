import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AutomationRuleCard } from "@/components/automation-rule-card";

const MOCK_RULE = {
  rule_id: "rule-1",
  name: "Flag High Scores",
  event_type: "submission.graded",
  conditions: [
    { field: "score", op: "gte", value: "90" },
    { field: "status", op: "equals", value: "submitted" },
  ],
  logic: "and" as const,
  actions: [
    { action_type: "notification" as const, config: { title: "High score!" } },
    { action_type: "webhook" as const, config: { url: "https://hook.example.com" } },
  ],
  enabled: true,
  last_triggered: "2026-10-28",
  match_count: 42,
};

const defaultProps = {
  rule: MOCK_RULE,
  onToggle: vi.fn(),
  onDelete: vi.fn(),
  onTest: vi.fn(),
};

describe("AutomationRuleCard", () => {
  it("renders rule name", () => {
    const { container } = render(<AutomationRuleCard {...defaultProps} />);
    expect(container.textContent).toContain("Flag High Scores");
  });

  it("renders event type", () => {
    const { container } = render(<AutomationRuleCard {...defaultProps} />);
    expect(container.textContent).toContain("submission.graded");
  });

  it("renders conditions with IF label", () => {
    const { container } = render(<AutomationRuleCard {...defaultProps} />);
    expect(container.textContent).toContain("IF");
    expect(container.textContent).toContain("score");
    expect(container.textContent).toContain("≥");
    expect(container.textContent).toContain("90");
    expect(container.textContent).toContain("status");
  });

  it("renders AND logic operator", () => {
    const { container } = render(<AutomationRuleCard {...defaultProps} />);
    expect(container.textContent).toContain("AND");
  });

  it("renders OR logic operator", () => {
    const orRule = { ...MOCK_RULE, logic: "or" as const };
    const { container } = render(<AutomationRuleCard {...defaultProps} rule={orRule} />);
    expect(container.textContent).toContain("OR");
  });

  it("renders actions with THEN label", () => {
    const { container } = render(<AutomationRuleCard {...defaultProps} />);
    expect(container.textContent).toContain("THEN");
    expect(container.textContent).toContain("Notification");
    expect(container.textContent).toContain("Webhook");
  });

  it("renders action icons", () => {
    const { container } = render(<AutomationRuleCard {...defaultProps} />);
    expect(container.textContent).toContain("🔔");
    expect(container.textContent).toContain("🌐");
  });

  it("renders match count", () => {
    const { container } = render(<AutomationRuleCard {...defaultProps} />);
    expect(container.textContent).toContain("42 matches");
  });

  it("renders last triggered", () => {
    const { container } = render(<AutomationRuleCard {...defaultProps} />);
    expect(container.textContent).toContain("2026-10-28");
  });

  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { container } = render(<AutomationRuleCard {...defaultProps} onToggle={onToggle} />);
    const toggle = container.querySelector("[role='switch']")!;
    fireEvent.click(toggle);
    expect(onToggle).toHaveBeenCalledWith("rule-1", false); // was enabled → toggle off
  });

  it("calls onDelete", () => {
    const onDelete = vi.fn();
    const { container } = render(<AutomationRuleCard {...defaultProps} onDelete={onDelete} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Delete",
    );
    fireEvent.click(btn!);
    expect(onDelete).toHaveBeenCalledWith("rule-1");
  });

  it("calls onTest (dry run)", () => {
    const onTest = vi.fn();
    const { container } = render(<AutomationRuleCard {...defaultProps} onTest={onTest} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Dry Run",
    );
    fireEvent.click(btn!);
    expect(onTest).toHaveBeenCalledWith("rule-1");
  });

  it("shows disabled styling", () => {
    const disabled = { ...MOCK_RULE, enabled: false };
    const { container } = render(<AutomationRuleCard {...defaultProps} rule={disabled} />);
    const toggle = container.querySelector("[role='switch']")!;
    expect(toggle.getAttribute("aria-checked")).toBe("false");
  });

  it("renders exists condition without value", () => {
    const rule = {
      ...MOCK_RULE,
      conditions: [{ field: "score", op: "exists", value: null }],
    };
    const { container } = render(<AutomationRuleCard {...defaultProps} rule={rule} />);
    expect(container.textContent).toContain("score");
    expect(container.textContent).toContain("exists");
  });
});
