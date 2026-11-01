import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-response-transformer-card";

describe("ConsumerApiResponseTransformerCard", () => {
  it("shows transforms", () => {
    const { container } = render(<Card consumerId="c1" renames={[{ from: "user_id", to: "id" }]} excludes={["debug"]} includeOnly={null} envelope={true} appName="App" />);
    expect(container.textContent).toContain("Response Transformer");
    expect(container.textContent).toContain("user_id → id");
    expect(container.textContent).toContain("debug");
    expect(container.textContent).toContain("Envelope: Yes");
  });
  it("shows no transforms", () => {
    const { container } = render(<Card consumerId="c1" renames={[]} excludes={[]} includeOnly={null} envelope={false} appName="App" />);
    expect(container.textContent).toContain("No transformations");
  });
});
