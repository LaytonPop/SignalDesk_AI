import { proxyToBackend } from "@/lib/backend";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = (await request.json()) as {
    reportDate?: string;
    lookbackHours?: number;
    topK?: number;
  };

  return proxyToBackend("/api/v1/reports/daily", {
    method: "POST",
    body: JSON.stringify({
      report_date: body.reportDate,
      lookback_hours: body.lookbackHours ?? 24,
      top_k: body.topK ?? 8,
    }),
  });
}
