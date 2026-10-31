import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiWebhookEventReplaySchedulerCard from "../src/components/api-developer-platform-sdk-api-platform-api-webhook-event-replay-scheduler-card";

const jobs = [{ job_id: "j1", destination: "https://a.com", total: 100, replayed: 75, failed_count: 5, status: "running", progress_pct: 80 }];

describe("Card", () => {
  it("shows replay jobs", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiWebhookEventReplaySchedulerCard jobs={jobs} activeCount={1} appName="App" />);
    expect(container.textContent).toContain("Replay Scheduler");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("j1");
    expect(container.textContent).toContain("75/100");
    expect(container.textContent).toContain("80%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiWebhookEventReplaySchedulerCard jobs={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No replay jobs");
  });
});
