# ref: https://gist.github.com/pudquick/eebc4d569100c8e3039bf3eae56bee4c

import objc
from Foundation import NSBundle

CoreServices = NSBundle.bundleWithIdentifier_("com.apple.CoreServices")

functions = [
    ("_LSCopyRunningApplicationArray", b"@I"),
    ("_LSCopyApplicationInformation", b"@I@@"),
]

constants = [
    ("_kLSDisplayNameKey", b"@"),
]

objc.loadBundleFunctions(CoreServices, globals(), functions)
objc.loadBundleVariables(CoreServices, globals(), constants)


def get_app_badges():
    kLSDefaultSessionID = 0xFFFFFFFE  # The actual value is `int -2`
    badge_label_key = "StatusLabel"  # TODO: Is there a `_kLS*` constant for this?

    app_asns = _LSCopyRunningApplicationArray(kLSDefaultSessionID)  # noqa: F821
    app_infos = [_LSCopyApplicationInformation(kLSDefaultSessionID, asn, None) for asn in app_asns]  # noqa: F821

    app_badges = {}
    for app_info in app_infos:
        if app_info and badge_label_key in app_info:
            app = app_info.get(_kLSDisplayNameKey)  # noqa: F821
            badge = get_badge(app_info, badge_label_key)
            if badge:
                app_badges[app] = badge

    return app_badges


def get_badge(app_info, badge_label_key):
    badge = app_info[badge_label_key].get("label", "<null>")
    if not badge or str(badge) == "<null>":
        return None

    try:
        return int(badge)
    except Exception:
        # Sometimes the badge can be a dot and we consider it as 1
        return 1
