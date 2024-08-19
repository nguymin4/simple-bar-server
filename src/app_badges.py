# Reference: https://gist.github.com/amomchilov/096ce5ceb9f4fca942ae0dd37066bc11
import objc
from Foundation import NSAutoreleasePool, NSBundle

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
    # https://github.com/WebKit/WebKit/blob/9502f8564a09c70c745630ae35bf1ee90bf21395/Source/WebCore/PAL/pal/spi/cocoa/LaunchServicesSPI.h#L44-L46
    kLSDefaultSessionID = 0xFFFFFFFE  # The actual value is `int -2`
    badge_label_key = "StatusLabel"  # TODO: Is there a `_kLS*` constant for this?

    pool = NSAutoreleasePool.alloc().init()
    app_asns = _LSCopyRunningApplicationArray(kLSDefaultSessionID)  # noqa: F821
    app_infos = [_LSCopyApplicationInformation(kLSDefaultSessionID, asn, None) for asn in app_asns]  # noqa: F821

    app_badges = {}
    for app_info in app_infos:
        if app_info and badge_label_key in app_info:
            badge = get_badge(app_info, badge_label_key)
            if badge:
                app = app_info.get(_kLSDisplayNameKey)  # noqa: F821
                app_badges[app] = badge

    del pool
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
