import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-mirror-card";

describe("RequestMirrorCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", mirror_url: "https://m.com", sample_rate: 0.5, enabled: true }];
    const { container } = render(<Card configs={configs} mirrored={5000} failed={10} appName="App" />);
    expect(container.textContent).toContain("Request Mirror");
    expect(container.textContent).toContain("5,000 mirrored");
    expect(container.textContent).toContain("50%");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} mirrored={0} failed={0} appName="App" />);
    expect(container.textContent).toContain("No mirror configs");
  });
});
