import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-dependency-injection-card";

describe("ConsumerApiDependencyInjectionCard", () => {
  it("shows bindings", () => {
    const bindings = [{ id: "b1", interfaceName: "IPaymentService", implementation: "StripePayment", scope: "singleton", active: true }];
    const { container } = render(<Card bindings={bindings} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Service Bindings");
    expect(container.textContent).toContain("IPaymentService");
    expect(container.textContent).toContain("StripePayment");
    expect(container.textContent).toContain("singleton");
  });
  it("shows empty", () => {
    const { container } = render(<Card bindings={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No bindings");
  });
});
