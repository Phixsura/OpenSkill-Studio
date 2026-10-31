import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WhRetryPanel } from "@/components/wh-retry-panel";

describe("WhRetryPanel", () => {
  it("renders", () => {
    const { container } = render(
      <WhRetryPanel succeeded={10} failed={2}
        pending={[
          { webhookId: "w1", attempt: 2, delayMs: 400, url: "https://hook.example.com" },
        ]} />
    );
    expect(container.textContent).toContain("Webhook Retries");
    expect(container.textContent).toContain("1 pending");
    expect(container.textContent).toContain("10 ok");
    expect(container.textContent).toContain("2 failed");
    expect(container.textContent).toContain("hook.example.com");
    expect(container.textContent).toContain("#2");
  });
});
