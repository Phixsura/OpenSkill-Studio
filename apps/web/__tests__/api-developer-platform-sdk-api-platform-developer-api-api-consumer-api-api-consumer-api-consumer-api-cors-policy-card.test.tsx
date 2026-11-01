import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-cors-policy-card";

describe("ConsumerApiCorsPolicyCard", () => {
  it("shows policy", () => {
    const { container } = render(<Card consumerId="c1" allowedOrigins={["https://app.example.com"]} allowedMethods={["GET", "POST"]} allowCredentials={true} maxAgeSec={86400} appName="App" />);
    expect(container.textContent).toContain("CORS Policy");
    expect(container.textContent).toContain("https://app.example.com");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("Credentials: Yes");
    expect(container.textContent).toContain("86400s");
  });
  it("shows wildcard", () => {
    const { container } = render(<Card consumerId="c1" allowedOrigins={["*"]} allowedMethods={["GET"]} allowCredentials={false} maxAgeSec={3600} appName="App" />);
    expect(container.textContent).toContain("*");
    expect(container.textContent).toContain("Credentials: No");
  });
});
