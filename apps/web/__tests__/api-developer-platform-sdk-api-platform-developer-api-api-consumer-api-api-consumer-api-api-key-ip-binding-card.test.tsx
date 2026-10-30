import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-api-key-ip-binding-card";

describe("ApiKeyIpBindingCard", () => {
  it("shows bindings", () => {
    const bindings = [{ key_id: "k1", consumer_id: "c1", allowed_ips: ["10.0.0.0/24"], enforce: true, violations: 3 }];
    const { container } = render(<Card bindings={bindings} appName="App" />);
    expect(container.textContent).toContain("Key IP Binding");
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("10.0.0.0/24");
    expect(container.textContent).toContain("3");
  });
  it("shows empty", () => {
    const { container } = render(<Card bindings={[]} appName="App" />);
    expect(container.textContent).toContain("No IP bindings");
  });
});
