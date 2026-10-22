# TikTok regional-signal observation plan

## Purpose and limits

Measure what is visibly observable when one regional setting changes at a time. A TikTok feed or UI response is **not** proof of the country TikTok assigned to an account. The plan does not infer a single decisive signal and does not automate engagement, evade restrictions, or test anti-integrity evasion.

Use a controlled test account owned by the researcher, with no valuable drafts or business activity. Prefer a controlled app that the researcher owns for API-level signal checks. Do not test on another person's account or collect their personal data.

## Readiness gate

The connected SM-A022F currently has Android 11/API 30, is locked, has no `su`, no LSPosed/Toki/TikTok package, and reports 32-bit ARM only. Therefore no Toki-on-TikTok experiment can run on the present setup. Keep this plan at preparation stage until the framework, package/version support, and device path have been independently verified. Bootloader unlock/root/partition changes require separate explicit approval and backup planning.

If later testing the Toki code, do not enable or evaluate its `isFromMockProvider() = false` behavior. It is outside this study's permitted scope. A safer first signal-validation experiment is a researcher-owned diagnostic app that records only the Android API values it receives, without any platform app or anti-detection behavior.

## Conditions

1. **Baseline:** ordinary device state; record actual system language/time zone, SIM/operator as voluntarily reported, actual location at city-level only, network type, and whether TikTok is installed. Do not collect phone number, IMEI, serial, account credentials, messages, or precise GPS coordinates.
2. **One-factor conditions (only where changed through normal, user-visible settings or a real-world change):** change only system language; only system time zone; only SIM/network by using a legitimately provisioned SIM; or only physical test location. Restore baseline between conditions. Record which settings were device-wide versus within TikTok's own UI.
3. **Optional Toki source-behavior condition:** only after a compatible framework and approved device setup exist, compare a single Toki option at a time using a controlled app the researcher owns. Do not use the mock-provider suppression path. TikTok testing with Toki requires additional validation of the framework/API and a controlled account; its result remains an observation, not a country-classification proof.

## Protocol

- Keep one test device, one test account, app version, network route, SIM, time-of-day window, and observation length constant where possible.
- Record a baseline before each changed condition. Change one independent variable, restart only the app when normal app behavior requires it, then observe the same surfaces.
- Run at least three sessions per condition, on separate app launches. Use the same fixed observation window (for example, first 10 minutes / first 20 visible feed cards). Do not like, follow, comment, share, search, or repeatedly watch content as an experimental input.
- Randomize the order of non-baseline conditions when practical, and restore baseline between them. Note that feeds may still adapt from passive viewing and prior account history.
- Capture only screenshots or notes needed to describe visible outcomes. Redact handles, faces, and other users' identifiers before sharing. Store raw notes locally and delete them when no longer needed.

## Variables and observations

| Category | Fields |
| --- | --- |
| Independent variable | One changed signal: language, time zone, real SIM/network condition, physical location, or (future controlled-app-only) one Toki app-level hook setting |
| Controlled variables | Device/build, TikTok version/build source, account age/history, app settings, time window, network type/route, SIM, observation duration, trial procedure |
| Observable outcomes | UI language, visible region-related labels, feed topic/category mix, surfaced local content, prompts/errors, crashes, and diagnostic app API values where applicable |
| Repeat count | Three independent sessions per condition minimum; report all trials, including null or inconsistent outcomes |
| Classification evidence | None from visible recommendations alone. Only describe outcomes as observed content/UI changes. Do not state that TikTok classified the account as a country without direct, authoritative evidence |

## Data record format

Use one row per session with fields:

```text
date_time_local,trial_id,condition,changed_factor,device_build,tiktok_version,network_type,
sim_condition,system_language,system_timezone,physical_city_only,app_restart,
observation_window,visible_language,region_labels,feed_category_counts,prompt_or_error,
crash_or_none,notes,redaction_done
```

Do not record account names, phone identifiers, exact coordinates, IP addresses, tokens, or private communications.

## Confounders and interpretation

Account age and prior watch history, follow graph, content availability, SIM roaming, carrier configuration, Wi-Fi/cellular IP geolocation, VPN/proxy use by other software, cached sessions, app build/store variant, time of day, language within content, creator audience, and recommendation randomness can all affect visible results. Keep these fixed or document them. Run the controlled diagnostic app separately from TikTok so Android API values are not confused with backend decisions.

Report descriptive changes only (for example, “more Arabic-language cards appeared in two of three sessions”). Do not claim a country assignment, causal feature, or guaranteed audience reach from the feed. Follow TikTok terms and applicable law; do not bypass access controls or account restrictions.
