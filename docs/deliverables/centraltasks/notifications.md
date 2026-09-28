# Day 18 notifications

The API persists an in-app notification when an authority changes a complaint
status or the SLA worker escalates it. Citizens can use their Clerk bearer
token to call:

- `GET /api/v1/notifications?limit=20&offset=0` (includes `unread_count`)
- `GET /api/v1/notifications?unread_only=true`
- `POST /api/v1/notifications/{notification_id}/read`

The status transaction queues `app.tasks.notification_tasks.send_status_update_email`
after commit. Run the normal Celery worker for email delivery. Configure the
backend environment with `CLERK_SECRET_KEY`, `SMTP_HOST`, and
`SMTP_FROM_EMAIL`; optional SMTP settings are `SMTP_PORT` (587),
`SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_STARTTLS` (true). If SMTP is not
configured, the worker records a warning and skips email while leaving the
in-app notification available. SMTP delivery has not been live-tested in this
repository environment.
