import AVFoundation
import AVKit
import AppKit
import Foundation

NSApplication.shared.activate(ignoringOtherApps: true)

class VideoPlayerDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var playerView: AVPlayerView!
    var player: AVPlayer!
    
    // Playlist management
    struct VideoEntry {
        let path: String
        let restaurantName: String
    }
    var videos: [VideoEntry] = []
    var currentVideoIndex: Int = 0

    // UI Elements
    var controlsView: NSView!
    var previousButton: NSButton!
    var nextButton: NSButton!
    var restaurantLabel: NSTextField!
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Need at least a restaurant name and video path pair
        guard CommandLine.arguments.count > 2 else {
            print("Usage: swift-video-player \"Restaurant Name 1\" video1.mp4 \"Restaurant Name 2\" video2.mp4 ...")
            NSApplication.shared.terminate(nil)
            return
        }
        
        // Parse arguments into video entries
        let args = Array(CommandLine.arguments.dropFirst())
        if args.count % 2 != 0 {
            print("Error: Each video must have a restaurant name")
            NSApplication.shared.terminate(nil)
            return
        }
        
        // Create video entries from pairs of arguments
        for i in stride(from: 0, to: args.count, by: 2) {
            videos.append(VideoEntry(path: args[i + 1], restaurantName: args[i]))
        }
        
        // Create the window
        let windowRect = NSRect(x: 0, y: 0, width: 800, height: 650)
        window = NSWindow(
            contentRect: windowRect,
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.level = .floating 
        // Create the main container view
        let containerView = NSView(frame: windowRect)
        window.contentView = containerView
        
        // Create the player view
        let playerRect = NSRect(x: 0, y: 50, width: windowRect.width, height: windowRect.height - 50)
        playerView = AVPlayerView(frame: playerRect)
        playerView.autoresizingMask = [.width, .height]
        playerView.controlsStyle = .floating
        playerView.showsFullScreenToggleButton = true
        containerView.addSubview(playerView)
        
        // Create controls view
        let controlsRect = NSRect(x: 0, y: 0, width: windowRect.width, height: 50)
        controlsView = NSView(frame: controlsRect)
        controlsView.autoresizingMask = [.width]
        containerView.addSubview(controlsView)
        
        // Create navigation buttons
        previousButton = NSButton(frame: NSRect(x: 10, y: 10, width: 100, height: 30))
        previousButton.title = "Previous"
        previousButton.bezelStyle = .rounded
        previousButton.target = self
        previousButton.action = #selector(previousVideo)
        controlsView.addSubview(previousButton)
        
        nextButton = NSButton(frame: NSRect(x: 120, y: 10, width: 100, height: 30))
        nextButton.title = "Next"
        nextButton.bezelStyle = .rounded
        nextButton.target = self
        nextButton.action = #selector(nextVideo)
        controlsView.addSubview(nextButton)
        
        // Create restaurant label
        restaurantLabel = NSTextField(frame: NSRect(x: 230, y: 15, width: 500, height: 20))
        restaurantLabel.isEditable = false
        restaurantLabel.isBordered = false
        restaurantLabel.backgroundColor = .clear
        restaurantLabel.font = NSFont.systemFont(ofSize: 14, weight: .bold)
        controlsView.addSubview(restaurantLabel)
        
        // Setup window
        window.title = "Video Player"
        window.center()
        window.makeKeyAndOrderFront(nil)
        
        // Start playing first video
        playCurrentVideo()
        
        // Set up keyboard event monitoring
        NSEvent.addLocalMonitorForEvents(matching: .keyDown) { event in
            self.handleKeyEvent(event)
            return event
        }
        
        // Print controls
        print("Controls:")
        print("Space: Play/Pause")
        print("Left Arrow: Seek backward 10 seconds")
        print("Right Arrow: Seek forward 10 seconds")
        print("N: Next video")
        print("P: Previous video")
        print("Q: Quit")
    }
    
    func playCurrentVideo() {
        guard currentVideoIndex >= 0 && currentVideoIndex < videos.count else {
            print("Invalid video index")
            return
        }
        
        let videoEntry = videos[currentVideoIndex]
        let videoURL = URL(fileURLWithPath: videoEntry.path)
        
        player = AVPlayer(url: videoURL)
        playerView.player = player
        
        // Update window title and restaurant label
        window.title = "Video Player - \(videoURL.lastPathComponent) [\(currentVideoIndex + 1)/\(videos.count)]"
        restaurantLabel.stringValue = videoEntry.restaurantName
        
        // Update button states
        previousButton.isEnabled = currentVideoIndex > 0
        nextButton.isEnabled = currentVideoIndex < videos.count - 1
        
        player.play()
    }
    
    @objc func previousVideo() {
        if currentVideoIndex > 0 {
            currentVideoIndex -= 1
            playCurrentVideo()
        }
    }
    
    @objc func nextVideo() {
        if currentVideoIndex < videos.count - 1 {
            currentVideoIndex += 1
            playCurrentVideo()
        }
    }
    
    func handleKeyEvent(_ event: NSEvent) {
        guard let characters = event.characters else { return }
        
        switch characters {
        case " ":
            // Toggle play/pause
            if player.rate == 0 {
                player.play()
                print("Playing")
            } else {
                player.pause()
                print("Paused")
            }
            
        case String(Character(UnicodeScalar(NSLeftArrowFunctionKey)!)):
            // Seek backward 10 seconds
            let currentTime = player.currentTime()
            let newTime = CMTimeAdd(currentTime, CMTime(seconds: -10, preferredTimescale: 1))
            player.seek(to: newTime)
            print("Seeking backward 10 seconds")
            
        case String(Character(UnicodeScalar(NSRightArrowFunctionKey)!)):
            // Seek forward 10 seconds
            let currentTime = player.currentTime()
            let newTime = CMTimeAdd(currentTime, CMTime(seconds: 10, preferredTimescale: 1))
            player.seek(to: newTime)
            print("Seeking forward 10 seconds")
            
        case "n", "N":
            nextVideo()
            
        case "p", "P":
            previousVideo()
            
        case "q", "Q":
            NSApplication.shared.terminate(nil)
            
        default:
            break
        }
    }
    
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }
}

// Create and start the application
let delegate = VideoPlayerDelegate()
let app = NSApplication.shared
app.delegate = delegate
app.run()