import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import PayloadValidatorCard from "../src/components/payload-validator-card";

const schemas = [
  {
    event_type: "user.created",
    required_count: 3,
    optional_count: 2,
    success_rate: 100,
    total_checks: 50,
  },
  {
    event_type: "order.placed",
    required_count: 5,
    optional_count: 1,
    success_rate: 85,
    total_checks: 20,
  },
];

describe("PayloadValidatorCard", () => {
  it("renders header", () => {
    const { container } = render(<PayloadValidatorCard schemas={schemas} appName="My App" />);
    expect(container.textContent).toContain("Payload Validation");
  });

  it("shows schema count and failing", () => {
    const { container } = render(<PayloadValidatorCard schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("2 schemas");
    expect(container.textContent).toContain("1 failing");
  });

  it("renders event types", () => {
    const { container } = render(<PayloadValidatorCard schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("user.created");
    expect(container.textContent).toContain("order.placed");
  });

  it("shows field counts", () => {
    const { container } = render(<PayloadValidatorCard schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("3req 2opt");
  });

  it("shows success rate", () => {
    const { container } = render(<PayloadValidatorCard schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("85%");
  });

  it("shows empty state", () => {
    const { container } = render(<PayloadValidatorCard schemas={[]} appName="App" />);
    expect(container.textContent).toContain("No payload schemas");
  });
});
