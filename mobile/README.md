# Android participant application

This directory is reserved for the Android participant client. Its first integration target is the published study configuration and the offline synchronization contract.

Planned first client capabilities:

- Enrollment through a link or QR code.
- Consent and permission capture.
- Download and local validation of a published configuration.
- Schema-driven questionnaire rendering.
- Local response queue and idempotent synchronization.

Flutter/Dart or native Android will be selected before implementation. No mobile source is included in this backend-first increment because Flutter/Dart is not installed in the current workspace environment.
