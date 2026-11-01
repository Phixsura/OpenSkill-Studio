import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformDeveloperApiOutputTransformerCard from "../src/components/api-developer-platform-sdk-api-platform-developer-api-output-transformer-card";

const rules = [{ rule_id: "r1", operation: "remove", field: "internal_id", applied_count: 5000 }];

describe("Card", () => {
  it("shows transformer", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformDeveloperApiOutputTransformerCard rules={rules} totalTransforms={10000} appName="App" />);
    expect(container.textContent).toContain("Output Transformer");
    expect(container.textContent).toContain("10,000 applied");
    expect(container.textContent).toContain("remove → internal_id");
    expect(container.textContent).toContain("5000×");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformDeveloperApiOutputTransformerCard rules={[]} totalTransforms={0} appName="App" />);
    expect(container.textContent).toContain("No transform rules");
  });
});
