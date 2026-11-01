import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-lifecycle-card";

describe("ConsumerLifecycleCard", () => {
  it("shows states", () => {
    const states = [{ state: "active", count: 45 }, { state: "onboarding", count: 5 }];
    const { container } = render(<Card states={states} totalConsumers={50} appName="App" />);
    expect(container.textContent).toContain("Consumer Lifecycle");
    expect(container.textContent).toContain("50 consumers");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("45");
  });
  it("shows empty", () => {
    const { container } = render(<Card states={[]} totalConsumers={0} appName="App" />);
    expect(container.textContent).toContain("No consumers");
  });
});
