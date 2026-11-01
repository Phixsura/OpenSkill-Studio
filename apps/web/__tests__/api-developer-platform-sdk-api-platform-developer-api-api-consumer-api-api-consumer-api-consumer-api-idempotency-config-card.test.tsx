import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-idempotency-config-card";

describe("ConsumerApiIdempotencyConfigCard", () => {
  it("shows config", () => {
    const { container } = render(<Card consumerId="c1" ttlSeconds={86400} maxKeyLength={128} requiredMethods={["POST", "PUT"]} enforce={true} keyHeader="Idempotency-Key" appName="App" />);
    expect(container.textContent).toContain("Idempotency Config");
    expect(container.textContent).toContain("Idempotency-Key");
    expect(container.textContent).toContain("24h");
    expect(container.textContent).toContain("128");
    expect(container.textContent).toContain("Required");
    expect(container.textContent).toContain("POST");
  });
  it("shows optional", () => {
    const { container } = render(<Card consumerId="c1" ttlSeconds={3600} maxKeyLength={64} requiredMethods={["POST"]} enforce={false} keyHeader="X-Idempotency" appName="App" />);
    expect(container.textContent).toContain("Optional");
  });
});
