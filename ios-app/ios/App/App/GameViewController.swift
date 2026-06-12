import UIKit
import WebKit
import Capacitor

/// Bridge view controller with media autoplay enabled: pygbag's loader probes
/// an <audio> element to detect "user media engagement" and WKWebView rejects
/// play() without a gesture by default, which would leave the game waiting on
/// a "click/touch to start" gate.
class GameViewController: CAPBridgeViewController {

    override func webViewConfiguration(for instanceConfiguration: InstanceConfiguration) -> WKWebViewConfiguration {
        let configuration = super.webViewConfiguration(for: instanceConfiguration)
        configuration.mediaTypesRequiringUserActionForPlayback = []
        configuration.allowsInlineMediaPlayback = true
        return configuration
    }
}
