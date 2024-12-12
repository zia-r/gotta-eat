import AVFoundation
import AVKit
import AppKit
import Foundation

class VideoPlayerDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var playerView: AVPlayerView!
    var player: AVPlayer!
    
    // Playlist management
    var videoFiles: [String] = []
    var currentVideoIndex: Int = 0
    
    // UI Elements
    var controlsView: NSView!
    var previousButton: NSButton!
    var nextButton: NSButton!
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Get video paths from command line arguments
        guard CommandLine.arguments.count > 1 else {
            print("Usage: swift-video-player <video_file_path1> [video_file_path2 ...]")
            NSApplication.shared.terminate(nil)
            return
        }
        
        // Store video files
        videoFiles = Array(CommandLine.arguments.dropFirst())
        
        // Create the window
        let windowRect = NSRect(x: 0, y: 0, width: 800, height: 650) // Extra height for controls
        window = NSWindow(
            contentRect: windowRect,
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        
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
        guard currentVideoIndex >= 0 && currentVideoIndex < videoFiles.count else {
            print("Invalid video index")
            return
        }
        
        let videoPath = videoFiles[currentVideoIndex]
        let videoURL = URL(fileURLWithPath: videoPath)
        
        player = AVPlayer(url: videoURL)
        playerView.player = player
        
        // Update window title with current video
        window.title = "Video Player - \(videoURL.lastPathComponent) [\(currentVideoIndex + 1)/\(videoFiles.count)]"
        
        // Update button states
        previousButton.isEnabled = currentVideoIndex > 0
        nextButton.isEnabled = currentVideoIndex < videoFiles.count - 1
        
        player.play()
    }
    
    @objc func previousVideo() {
        if currentVideoIndex > 0 {
            currentVideoIndex -= 1
            playCurrentVideo()
        }
    }
    
    @objc func nextVideo() {
        if currentVideoIndex < videoFiles.count - 1 {
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