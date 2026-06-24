from prometheus_client import Counter, Histogram

HTTP_REQUESTS = Counter(
    "claimops_http_requests_total", "HTTP requests", ["method", "route", "status"]
)
HTTP_DURATION = Histogram(
    "claimops_http_request_duration_seconds", "HTTP request latency", ["method", "route"]
)
