import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-webhook-payload-validator-card";

describe("PayloadValidatorCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card stats={{ valid: 9500, invalid: 500, validation_rate: 95 }} maxPayloadKb={1024} appName="App" />);
    expect(container.textContent).toContain("Payload Validator");
    expect(container.textContent).toContain("9,500");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("95%");
  });
  it("shows max size", () => {
    const { container } = render(<Card stats={{ valid: 0, invalid: 0, validation_rate: 0 }} maxPayloadKb={512} appName="App" />);
    expect(container.textContent).toContain("max 512 KB");
  });
});
