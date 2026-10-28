import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ABTestCard from "../src/components/ab-test-card";

const activeExp = {
  experiment_id: "exp-1",
  name: "Button Color Test",
  active: true,
  variants: [
    { name: "control", exposures: 1000, conversions: 50, conversion_rate: 5.0 },
    { name: "treatment", exposures: 1000, conversions: 80, conversion_rate: 8.0 },
  ],
};

const stoppedExp = {
  experiment_id: "exp-2",
  name: "Layout Test",
  active: false,
  variants: [
    { name: "A", exposures: 500, conversions: 25, conversion_rate: 5.0 },
    { name: "B", exposures: 500, conversions: 30, conversion_rate: 6.0 },
  ],
};

describe("ABTestCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ABTestCard experiments={[activeExp]} appName="My App" />);
    expect(container.textContent).toContain("A/B Tests");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(
      <ABTestCard experiments={[activeExp, stoppedExp]} appName="App" />,
    );
    expect(container.textContent).toContain("1 active");
  });

  it("renders experiment name", () => {
    const { container } = render(<ABTestCard experiments={[activeExp]} appName="App" />);
    expect(container.textContent).toContain("Button Color Test");
  });

  it("shows running/stopped badges", () => {
    const { container } = render(
      <ABTestCard experiments={[activeExp, stoppedExp]} appName="App" />,
    );
    expect(container.textContent).toContain("Running");
    expect(container.textContent).toContain("Stopped");
  });

  it("renders variant names and conversion rates", () => {
    const { container } = render(<ABTestCard experiments={[activeExp]} appName="App" />);
    expect(container.textContent).toContain("control");
    expect(container.textContent).toContain("treatment");
    expect(container.textContent).toContain("5.0%");
    expect(container.textContent).toContain("8.0%");
  });

  it("shows conversion counts", () => {
    const { container } = render(<ABTestCard experiments={[activeExp]} appName="App" />);
    expect(container.textContent).toContain("50/1.0K");
    expect(container.textContent).toContain("80/1.0K");
  });

  it("shows empty state", () => {
    const { container } = render(<ABTestCard experiments={[]} appName="App" />);
    expect(container.textContent).toContain("No experiments");
  });
});
